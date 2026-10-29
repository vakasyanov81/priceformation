"""SOAP-клиент API Форточек: шины и диски по складам → JSON-строки прайса (reader «json»)."""

import json
from collections.abc import Callable, Iterator, Mapping, Sequence
from contextlib import closing
from functools import partial
from html import escape
from http.client import HTTPException, HTTPSConnection
from pathlib import Path
from typing import Any, NamedTuple, Protocol
from urllib.parse import urlsplit
from xml.etree import ElementTree  # nosec B405 — ответ доверенного HTTPS-сервиса, не пользовательский ввод

from domain.exceptions import CoreExceptionError
from domain.four_tochki import FourTochkiApiWarehouse, FourTochkiWarehouse

type JsonRow = dict[str, Any]

_VENDOR_FOLDER = 'four_tochki'
_NAMESPACE = 'Wcf.ClientService.Client.WebAPI.TS3'
_TIRE_FILENAME = 'tire.json'
_DISK_FILENAME = 'disk.json'
_PAGE_SIZE = 2000
_TIRE_CONTRACT_NS = 'http://schemas.datacontract.org/2004/07/TS3.Domain.Models.Client.ClientSoapService.SearchTires'
_DISK_CONTRACT_NS = 'http://schemas.datacontract.org/2004/07/TS3.Domain.Models.Client.ClientSoapService.SearchDiscs'
_ARRAY_NS = 'http://schemas.microsoft.com/2003/10/Serialization/Arrays'


def _filter_field(ns: str, name: str, inner: str) -> str:
    """Поле фильтра: WCF принимает его только в пространстве имён контракта, иначе игнорирует."""
    return f'<{name} xmlns="{ns}">{inner}</{name}>'


def _warehouse_field(ns: str, warehouses: Sequence[FourTochkiWarehouse]) -> str:
    ids = ''.join(f'<int xmlns="{_ARRAY_NS}">{warehouse.id}</int>' for warehouse in warehouses)
    return _filter_field(ns, 'wrh_list', ids)


def _paid_delivery_field(ns: str) -> str:
    return _filter_field(ns, 'include_paid_delivery', 'true')


def _tire_filter(warehouses: Sequence[FourTochkiWarehouse]) -> str:
    return _warehouse_field(_TIRE_CONTRACT_NS, warehouses) + _paid_delivery_field(_TIRE_CONTRACT_NS)


def _disk_filter(warehouses: Sequence[FourTochkiWarehouse]) -> str:
    return (
        _filter_field(
            _DISK_CONTRACT_NS,
            'rim_vid_name_list',
            ''.join(f'<string xmlns="{_ARRAY_NS}">{rim_type}</string>' for rim_type in ('car', 'truck', 'specteh')),
        )
        + _warehouse_field(_DISK_CONTRACT_NS, warehouses)
        + _paid_delivery_field(_DISK_CONTRACT_NS)
    )


_SEASONS = {'w': 'Зимняя', 's': 'Летняя', 'u': 'Всесезонная'}
_TIRE_TYPES = {'car': 'Легковая', 'truck': 'Грузовая', 'moto': 'Мото', 'specteh': 'Спецтехника'}
_DISK_TYPES = {'0': 'Литой', '1': 'Штампованный', '2': 'Кованный'}
_MSG_CONNECTION_FAILED = (
    'Не удалось подключиться к API Форточек. Проверьте интернет-соединение и параметры подключения.'
)
_MSG_RESPONSE_FAILED = 'API Форточек вернул ответ, который не удалось разобрать.'
_MSG_API_ERROR = 'API Форточек вернул ошибку. Подробности в логе.'
_MSG_HTTP_STATUS = 'API Форточек ответил HTTP-статусом, отличным от 2xx.'
_HTTP_TIMEOUT_SECONDS = 60
_HTTP_STATUS_OK_FROM = 200
_HTTP_STATUS_OK_TO = 299
_BODY_SNIPPET_LIMIT = 300


class FourTochkiApiAuth(Protocol):
    """Адрес SOAP-сервиса и логин с паролем."""

    @property
    def endpoint(self) -> str: ...

    @property
    def login(self) -> str: ...

    @property
    def password(self) -> str: ...


class FourTochkiApiConnectionError(CoreExceptionError):
    """Four Tochki API host is unreachable."""

    __MESSAGE__ = _MSG_CONNECTION_FAILED


class FourTochkiApiError(CoreExceptionError):
    """Four Tochki API вернул error или ответ не разобрать."""

    __MESSAGE__ = _MSG_API_ERROR


def fetch_warehouses(api: FourTochkiApiAuth) -> list[FourTochkiApiWarehouse]:
    """Справочник складов, доступных клиенту (GetWarehouses): ID и название."""
    answer = _call_method(api, 'GetWarehouses')
    return [
        FourTochkiApiWarehouse(id=_int(_child_text(element, 'id')), name=_child_text(element, 'name'))
        for element in answer.iter()
        if _local(element.tag) == 'WarehouseInfo'
    ]


def warehouses_by_id(warehouses: Sequence[FourTochkiWarehouse]) -> Mapping[int, FourTochkiWarehouse]:
    """Склады по ID из API."""
    return {warehouse.id: warehouse for warehouse in warehouses}


def download_catalogs(*, dest_dir: Path, api: FourTochkiApiAuth, warehouses: Sequence[FourTochkiWarehouse]) -> None:
    """GetFindTyre / GetFindDisk постранично → dest_dir/tire.json, disk.json."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    by_id = warehouses_by_id(warehouses)
    tire_rows = _rows(
        _fetch_positions(api, 'GetFindTyre', _tire_filter(warehouses), 'TyrePriceRest'),
        partial(_tire_rows, warehouses=by_id),
    )
    disk_rows = _rows(
        _fetch_positions(api, 'GetFindDisk', _disk_filter(warehouses), 'DiskPriceRest'),
        partial(_disk_rows, warehouses=by_id),
    )
    _write_rows(dest_dir / _TIRE_FILENAME, tire_rows)
    _write_rows(dest_dir / _DISK_FILENAME, disk_rows)


def _write_rows(path: Path, rows: list[JsonRow]) -> None:
    """JSON с отступами и кириллицей как есть — файлы читаются глазами."""
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8')


def _rows(
    positions: Iterator[ElementTree.Element],
    to_rows: Callable[[ElementTree.Element], list[JsonRow]],
) -> list[JsonRow]:
    """Строки прайса по всем позициям: одна позиция даёт строку на каждый склад."""
    return [row for position in positions for row in to_rows(position)]


def _fetch_positions(
    api: FourTochkiApiAuth,
    method: str,
    filter_xml: str,
    position_tag: str,
) -> Iterator[ElementTree.Element]:
    """Все страницы поиска по одному фильтру; страница — до _PAGE_SIZE позиций."""
    page = 0
    while True:
        answer = _call_method(api, method, _search_params(filter_xml, page))
        yield from (element for element in answer.iter() if _local(element.tag) == position_tag)
        page += 1
        if page >= _int(_child_text(answer, 'totalPages')):
            return


def _search_params(filter_xml: str, page: int) -> str:
    """Параметры поиска: фильтр и страница."""
    return f'<filter>{filter_xml}</filter><page>{page}</page><pageSize>{_PAGE_SIZE}</pageSize>'


def _call_method(api: FourTochkiApiAuth, method: str, params_xml: str = '') -> ElementTree.Element:
    """Один вызов метода; возвращает элемент <…Result> и проверяет error в ответе."""
    body = f'<login>{escape(api.login)}</login><password>{escape(api.password)}</password>{params_xml}'
    root = _parse_response(_post(api, method, _envelope(method, body)))
    answer = _result_element(root, method)
    _raise_on_error(answer, method)
    return answer


def _result_element(root: ElementTree.Element, method: str) -> ElementTree.Element:
    """Элемент <…Result> метода; его нет — ответ не от этого метода."""
    for element in root.iter():
        if _local(element.tag) == f'{method}Result':
            return element
    raise FourTochkiApiError(detail=f'{_MSG_RESPONSE_FAILED} method={method}')


def _envelope(method: str, body: str) -> bytes:
    """SOAP 1.1 конверт вызова метода сервиса."""
    xml_text = (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">'
        f'<s:Body><{method} xmlns="{_NAMESPACE}">{body}</{method}></s:Body></s:Envelope>'
    )
    return xml_text.encode()


class _HttpReply(NamedTuple):
    """Статус, причина и тело ответа HTTP."""

    status: int
    reason: str
    payload: bytes


def _post(api: FourTochkiApiAuth, method: str, envelope: bytes) -> bytes:
    """POST SOAP-конверта; сетевые ошибки и таймаут — ошибка подключения, не-2xx — ошибка API."""
    try:
        reply = _send(api.endpoint, method, envelope)
    except (OSError, HTTPException) as exc:
        detail = f'endpoint={api.endpoint} method={method}\n{exc!r}'
        raise FourTochkiApiConnectionError(detail=detail) from exc
    _raise_on_http_status(reply, method)
    return reply.payload


def _send(endpoint: str, method: str, envelope: bytes) -> _HttpReply:
    """Один HTTPS-запрос с таймаутом; тело читается целиком до закрытия соединения."""
    url = urlsplit(endpoint)
    headers = {
        'Content-Type': 'text/xml; charset=utf-8',
        'SOAPAction': f'"{_NAMESPACE}/ClientService/{method}"',
    }
    with closing(HTTPSConnection(url.netloc, timeout=_HTTP_TIMEOUT_SECONDS)) as connection:
        connection.request('POST', url.path, body=envelope, headers=headers)
        response = connection.getresponse()
        return _HttpReply(response.status, response.reason, response.read())


def _raise_on_http_status(reply: _HttpReply, method: str) -> None:
    """Не-2xx ответ (например, 504 с HTML от прокси) — ошибка API со статусом и началом тела."""
    if _HTTP_STATUS_OK_FROM <= reply.status <= _HTTP_STATUS_OK_TO:
        return
    snippet = reply.payload[:_BODY_SNIPPET_LIMIT].decode('utf-8', 'replace')
    raise FourTochkiApiError(
        detail=f'{_MSG_HTTP_STATUS} status={reply.status} {reply.reason} method={method}\n{snippet}',
    )


def _parse_response(payload: bytes) -> ElementTree.Element:
    """Ответ доверенного HTTPS-сервиса Форточек, не пользовательский ввод."""
    try:
        return ElementTree.fromstring(payload)  # noqa: S314  # nosec B314 — ответ доверенного HTTPS-сервиса
    except ElementTree.ParseError as exc:
        raise FourTochkiApiError(detail=f'{_MSG_RESPONSE_FAILED}\n{exc!r}') from exc


def _raise_on_error(answer: ElementTree.Element, method: str) -> None:
    """Элемент error с комментарием — ошибка API; nil — успех."""
    for element in answer:
        if _local(element.tag) != 'error':
            continue
        comment = _child_text(element, 'comment')
        if comment:
            raise FourTochkiApiError(detail=f'method={method} code={_child_text(element, "code")} comment={comment}')


def _tire_rows(position: ElementTree.Element, warehouses: Mapping[int, FourTochkiWarehouse]) -> list[JsonRow]:
    """Шина → строки по складам; тип и сезон приведены к словарю прайса."""
    base = _position_fields(position)
    base.update(
        season=_SEASONS.get(_child_text(position, 'season'), ''),
        spike='Да' if _child_text(position, 'thorn') == 'true' else '',
        tire_type=_TIRE_TYPES.get(_child_text(position, 'type'), _child_text(position, 'type')),
    )
    return _warehouse_rows(position, base, warehouses)


def _disk_rows(position: ElementTree.Element, warehouses: Mapping[int, FourTochkiWarehouse]) -> list[JsonRow]:
    """Диск → строки по складам; тип диска приведён к словарю прайса."""
    base = _position_fields(position)
    base.update(
        color=_child_text(position, 'color'),
        disk_type=_DISK_TYPES.get(_child_text(position, 'type'), ''),
    )
    return _warehouse_rows(position, base, warehouses)


def _position_fields(position: ElementTree.Element) -> JsonRow:
    """Общие поля позиции (шина и диск): код, название, производитель, модель."""
    return {
        'code': _child_text(position, 'code'),
        'title': _child_text(position, 'name'),
        'manufacturer_name': _child_text(position, 'marka'),
        'model': _child_text(position, 'model'),
    }


def _warehouse_rows(
    position: ElementTree.Element,
    base: JsonRow,
    warehouses: Mapping[int, FourTochkiWarehouse],
) -> list[JsonRow]:
    """Остатки и цены по каждому складу из whpr → строки с общими полями позиции.

    Склад вне настроек пропускается: список складов задаёт настройки, а не ответ API.
    """
    rows: list[JsonRow] = []
    for whpr in position.iter():
        if _local(whpr.tag) != 'wh_price_rest':
            continue
        warehouse = warehouses.get(_int(_child_text(whpr, 'wrh')))
        if warehouse is None:
            continue
        rows.append(
            {
                **base,
                'price_opt': _float(_child_text(whpr, 'price')),
                'price_recommended': _float(_child_text(whpr, 'price_rozn')),
                'rest_count': _int(_child_text(whpr, 'rest')),
                **_warehouse_fields(warehouse),
            },
        )
    return rows


def _warehouse_fields(warehouse: FourTochkiWarehouse) -> JsonRow:
    """Поля склада из настроек: название для прайса, группа объединения, наличие и срок."""
    return {
        'warehouse_id': warehouse.id,
        'warehouse_name': warehouse.name,
        'warehouse_group': warehouse.merge_group,
        'available': warehouse.available,
        'delivery_period': warehouse.delivery_period,
    }


def _local(tag: str) -> str:
    """Имя тега без пространства имён."""
    return tag.rsplit('}', 1)[-1]


def _child_text(element: ElementTree.Element, name: str) -> str:
    """Текст первого дочернего элемента с указанным локальным именем; пусто, если нет."""
    for child in element:
        if _local(child.tag) == name:
            return (child.text or '').strip()
    return ''


def _int(text: str) -> int:
    return int(text or 0)


def _float(text: str) -> float:
    return float(text or 0)
