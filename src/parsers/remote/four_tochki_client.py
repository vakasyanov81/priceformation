"""SOAP-клиент API Форточек: шины и диски по складам → JSON-строки прайса (reader «json»)."""

import json
from collections.abc import Callable, Iterator
from contextlib import closing
from html import escape
from http.client import HTTPException, HTTPSConnection
from pathlib import Path
from typing import Any, Protocol
from urllib.parse import urlsplit
from xml.etree import ElementTree  # nosec B405 — ответ доверенного HTTPS-сервиса, не пользовательский ввод

from domain.config_context import get_config_provider
from domain.exceptions import CoreExceptionError

type JsonRow = dict[str, Any]

_VENDOR_FOLDER = 'four_tochki'
_NAMESPACE = 'Wcf.ClientService.Client.WebAPI.TS3'
_TIRE_FILENAME = 'tire.json'
_DISK_FILENAME = 'disk.json'
_PAGE_SIZE = 2000
_TIRE_CONTRACT_NS = 'http://schemas.datacontract.org/2004/07/TS3.Domain.Models.Client.ClientSoapService.SearchTires'
_DISK_CONTRACT_NS = 'http://schemas.datacontract.org/2004/07/TS3.Domain.Models.Client.ClientSoapService.SearchDiscs'
_ARRAY_NS = 'http://schemas.microsoft.com/2003/10/Serialization/Arrays'
# Склады Новосибирска, Бердска и Искитима из GetWarehouses: собственный склад «Новосибирск» (1423)
# и склады ОХ (ответственное хранение).
_NSK_REGION_WAREHOUSE_IDS = (
    276,
    2167,
    912,
    1423,
    364,
    917,
    1135,
    1254,
    283,
    918,
    1166,
    1860,
    2625,
    1154,
    871,
    1167,
    2224,
    2347,
    3826,
    1604,
    2623,
    2145,
)


def _filter_field(ns: str, name: str, inner: str) -> str:
    """Поле фильтра: WCF принимает его только в пространстве имён контракта, иначе игнорирует."""
    return f'<{name} xmlns="{ns}">{inner}</{name}>'


def _warehouse_field(ns: str) -> str:
    ids = ''.join(f'<int xmlns="{_ARRAY_NS}">{warehouse_id}</int>' for warehouse_id in _NSK_REGION_WAREHOUSE_IDS)
    return _filter_field(ns, 'wrh_list', ids)


def _paid_delivery_field(ns: str) -> str:
    return _filter_field(ns, 'include_paid_delivery', 'true')


_TIRE_FILTER = _warehouse_field(_TIRE_CONTRACT_NS) + _paid_delivery_field(_TIRE_CONTRACT_NS)
_DISK_FILTER = (
    _filter_field(
        _DISK_CONTRACT_NS,
        'rim_vid_name_list',
        ''.join(f'<string xmlns="{_ARRAY_NS}">{rim_type}</string>' for rim_type in ('car', 'truck', 'specteh')),
    )
    + _warehouse_field(_DISK_CONTRACT_NS)
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


def load_remote_vendor_data(*, api: FourTochkiApiAuth) -> None:
    """Выгрузить шины и диски в file_prices/four_tochki."""
    dest_dir = Path(get_config_provider().price_folder(_VENDOR_FOLDER))
    download_catalogs(dest_dir=dest_dir, api=api)


def download_catalogs(*, dest_dir: Path, api: FourTochkiApiAuth) -> None:
    """GetFindTyre / GetFindDisk постранично → dest_dir/tire.json, disk.json."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    tire_rows = _rows(_fetch_positions(api, 'GetFindTyre', _TIRE_FILTER, 'TyrePriceRest'), _tire_rows)
    disk_rows = _rows(_fetch_positions(api, 'GetFindDisk', _DISK_FILTER, 'DiskPriceRest'), _disk_rows)
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
        answer = _call_method(api, method, filter_xml, page)
        yield from (element for element in answer.iter() if _local(element.tag) == position_tag)
        page += 1
        if page >= _int(_child_text(answer, 'totalPages')):
            return


def _call_method(api: FourTochkiApiAuth, method: str, filter_xml: str, page: int) -> ElementTree.Element:
    """Один вызов поиска; возвращает элемент <…Result> и проверяет error в ответе."""
    body = (
        f'<login>{escape(api.login)}</login><password>{escape(api.password)}</password>'
        f'<filter>{filter_xml}</filter><page>{page}</page><pageSize>{_PAGE_SIZE}</pageSize>'
    )
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


def _post(api: FourTochkiApiAuth, method: str, envelope: bytes) -> bytes:
    """POST SOAP-конверта; сетевые ошибки — ошибка подключения."""
    url = urlsplit(api.endpoint)
    headers = {
        'Content-Type': 'text/xml; charset=utf-8',
        'SOAPAction': f'"{_NAMESPACE}/ClientService/{method}"',
    }
    try:
        with closing(HTTPSConnection(url.netloc)) as connection:
            connection.request('POST', url.path, body=envelope, headers=headers)
            return connection.getresponse().read()
    except (OSError, HTTPException) as exc:
        detail = f'endpoint={api.endpoint} method={method}\n{exc!r}'
        raise FourTochkiApiConnectionError(detail=detail) from exc


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


def _tire_rows(position: ElementTree.Element) -> list[JsonRow]:
    """Шина → строки по складам; тип и сезон приведены к словарю прайса."""
    base = _position_fields(position)
    base.update(
        season=_SEASONS.get(_child_text(position, 'season'), ''),
        spike='Да' if _child_text(position, 'thorn') == 'true' else '',
        tire_type=_TIRE_TYPES.get(_child_text(position, 'type'), _child_text(position, 'type')),
    )
    return _warehouse_rows(position, base)


def _disk_rows(position: ElementTree.Element) -> list[JsonRow]:
    """Диск → строки по складам; тип диска приведён к словарю прайса."""
    base = _position_fields(position)
    base.update(
        color=_child_text(position, 'color'),
        disk_type=_DISK_TYPES.get(_child_text(position, 'type'), ''),
    )
    return _warehouse_rows(position, base)


def _position_fields(position: ElementTree.Element) -> JsonRow:
    """Общие поля позиции (шина и диск): код, название, производитель, модель."""
    return {
        'code': _child_text(position, 'code'),
        'title': _child_text(position, 'name'),
        'manufacturer_name': _child_text(position, 'marka'),
        'model': _child_text(position, 'model'),
    }


def _warehouse_rows(position: ElementTree.Element, base: JsonRow) -> list[JsonRow]:
    """Остатки и цены по каждому складу из whpr → строки с общими полями позиции."""
    rows: list[JsonRow] = []
    for whpr in position.iter():
        if _local(whpr.tag) != 'wh_price_rest':
            continue
        rows.append(
            {
                **base,
                'price_opt': _float(_child_text(whpr, 'price')),
                'price_recommended': _float(_child_text(whpr, 'price_rozn')),
                'rest_count': _int(_child_text(whpr, 'rest')),
                'warehouse_id': _int(_child_text(whpr, 'wrh')),
            },
        )
    return rows


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
