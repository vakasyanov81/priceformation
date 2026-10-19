"""SOAP-клиент Форточек: точный состав запроса, тексты ошибок и разбор типов, сезонов и числовых полей."""

import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from domain.exceptions import CoreExceptionError
from infrastructure.config.four_tochki_api_config import FourTochkiApiConfig
from parsers.remote.four_tochki_client import (
    FourTochkiApiConnectionError,
    FourTochkiApiError,
    _post,
    download_catalogs,
    fetch_warehouses,
)
from parsers.remote.four_tochki_warehouses import FourTochkiApiWarehouse, FourTochkiWarehouse

_API = FourTochkiApiConfig(endpoint='https://api.test/WCF/ClientService.svc', login='user', password='secret')
_WAREHOUSE = FourTochkiWarehouse(id=7, name='Склад')
_SECOND = FourTochkiWarehouse(id=9, name='Второй')
_POST = 'parsers.remote.four_tochki_client._post'
_HTTPS = 'parsers.remote.four_tochki_client.HTTPSConnection'
_NS_RESULT = 'xmlns:a="x" xmlns:b="y" xmlns:i="z"'
_SERVICE_NS = 'Wcf.ClientService.Client.WebAPI.TS3'
_ARRAY_NS = 'http://schemas.microsoft.com/2003/10/Serialization/Arrays'
_TIRE_NS = 'http://schemas.datacontract.org/2004/07/TS3.Domain.Models.Client.ClientSoapService.SearchTires'
_DISK_NS = 'http://schemas.datacontract.org/2004/07/TS3.Domain.Models.Client.ClientSoapService.SearchDiscs'
_WRH_IDS = (7, 9)
_RIM_TYPES = ('car', 'truck', 'specteh')
_ERROR = '<a:error><a:code>30</a:code><a:comment>Ошибка авторизации.</a:comment></a:error>'
_NIL_ERROR = '<a:error i:nil="true"/>'
_WHPR = (
    '<b:wh_price_rest><b:price>10</b:price><b:price_rozn>20</b:price_rozn><b:rest>3</b:rest><b:wrh>7</b:wrh>'
    '</b:wh_price_rest>'
)


def _response(method: str, result_body: str) -> bytes:
    return (
        '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body>'
        f'<{method}Response xmlns="{_SERVICE_NS}"><{method}Result {_NS_RESULT}>{result_body}</{method}Result>'
        f'</{method}Response></s:Body></s:Envelope>'
    ).encode()


def _page(method: str, positions: str = '') -> bytes:
    return _response(
        method, f'{_NIL_ERROR}<a:price_rest_list>{positions}</a:price_rest_list><a:totalPages>1</a:totalPages>'
    )


def _tire(season: str = 'w', thorn: str = 'true', tire_type: str = 'car', whpr: str = _WHPR) -> str:
    return (
        '<a:TyrePriceRest><a:code>1</a:code><a:marka>M</a:marka><a:model>Mod</a:model><a:name>N</a:name>'
        f'<a:season>{season}</a:season><a:thorn>{thorn}</a:thorn><a:type>{tire_type}</a:type>'
        f'<a:whpr>{whpr}</a:whpr></a:TyrePriceRest>'
    )


def _disk(disk_type: str = '0', whpr: str = _WHPR) -> str:
    return (
        '<a:DiskPriceRest><a:code>1</a:code><a:color>C</a:color><a:marka>M</a:marka><a:model>Mod</a:model>'
        f'<a:name>N</a:name><a:type>{disk_type}</a:type><a:whpr>{whpr}</a:whpr></a:DiskPriceRest>'
    )


type _Rows = list[dict[str, Any]]


def _download_pages(tmp_path: Path, tire_page: bytes, disk_page: bytes) -> tuple[_Rows, _Rows]:
    with patch(_POST, side_effect=[tire_page, disk_page]):
        download_catalogs(dest_dir=tmp_path, api=_API, warehouses=(_WAREHOUSE,))
    return (
        json.loads((tmp_path / 'tire.json').read_text(encoding='utf-8')),
        json.loads((tmp_path / 'disk.json').read_text(encoding='utf-8')),
    )


def _tires(tmp_path: Path, positions: str = '') -> _Rows:
    """Строки tire.json после выгрузки шин с указанными позициями (дисков нет)."""
    return _download_pages(tmp_path, _page('GetFindTyre', positions), _page('GetFindDisk'))[0]


def _disks(tmp_path: Path, positions: str = '') -> _Rows:
    """Строки disk.json после выгрузки дисков с указанными позициями (шин нет)."""
    return _download_pages(tmp_path, _page('GetFindTyre'), _page('GetFindDisk', positions))[1]


def _envelope(method: str, search: str) -> bytes:
    return (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">'
        f'<s:Body><{method} xmlns="{_SERVICE_NS}"><login>user</login><password>secret</password>{search}'
        f'</{method}></s:Body></s:Envelope>'
    ).encode()


def _wrh(ns: str) -> str:
    ids = ''.join(f'<int xmlns="{_ARRAY_NS}">{wrh}</int>' for wrh in _WRH_IDS)
    return f'<wrh_list xmlns="{ns}">{ids}</wrh_list>'


def _paid(ns: str) -> str:
    return f'<include_paid_delivery xmlns="{ns}">true</include_paid_delivery>'


def test_search_envelopes_match_contract_exactly(tmp_path: Path) -> None:
    """Запросы GetFindTyre / GetFindDisk сверяются целиком: фильтр, страница, размер страницы."""
    with patch(_POST, side_effect=[_page('GetFindTyre'), _page('GetFindDisk')]) as mock_post:
        download_catalogs(dest_dir=tmp_path, api=_API, warehouses=(_WAREHOUSE, _SECOND))

    tire_envelope, disk_envelope = (call.args[2] for call in mock_post.call_args_list)
    page = '<page>0</page><pageSize>2000</pageSize>'
    tire_filter = f'{_wrh(_TIRE_NS)}{_paid(_TIRE_NS)}'
    assert tire_envelope == _envelope('GetFindTyre', f'<filter>{tire_filter}</filter>{page}')
    rim_types = ''.join(f'<string xmlns="{_ARRAY_NS}">{rim}</string>' for rim in _RIM_TYPES)
    rim_filter = f'<rim_vid_name_list xmlns="{_DISK_NS}">{rim_types}</rim_vid_name_list>'
    disk_filter = f'{rim_filter}{_wrh(_DISK_NS)}{_paid(_DISK_NS)}'
    assert disk_envelope == _envelope('GetFindDisk', f'<filter>{disk_filter}</filter>{page}')
    assert [call.args[1] for call in mock_post.call_args_list] == ['GetFindTyre', 'GetFindDisk']


def test_post_sends_exact_request() -> None:
    """POST: метод, путь, тело и заголовки — точные значения, имена заголовков в регистре контракта."""
    connection = MagicMock()
    connection.getresponse.return_value.status = 200
    connection.getresponse.return_value.read.return_value = _page('GetFindTyre')
    with patch(_HTTPS, return_value=connection):
        answer = _post(_API, 'GetFindTyre', b'<body/>')

    assert answer == _page('GetFindTyre')
    connection.request.assert_called_once_with(
        'POST',
        '/WCF/ClientService.svc',
        body=b'<body/>',
        headers={
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': f'"{_SERVICE_NS}/ClientService/GetFindTyre"',
        },
    )
    connection.close.assert_called_once_with()


def test_connection_error_detail_names_endpoint_and_method() -> None:
    """В лог ошибки подключения попадают адрес, метод и исходное исключение."""
    with (
        patch(_HTTPS, side_effect=OSError('network down')),
        patch.object(CoreExceptionError, 'to_log') as to_log,
        pytest.raises(FourTochkiApiConnectionError),
    ):
        fetch_warehouses(_API)

    to_log.assert_called_once_with(
        "endpoint=https://api.test/WCF/ClientService.svc method=GetWarehouses\nOSError('network down')"
    )


def test_api_error_detail_has_method_code_and_comment() -> None:
    """Ошибка API: в лог идут метод, код и комментарий; тип и сообщение для пользователя фиксированы."""
    answer = _response('GetWarehouses', f'{_ERROR}')
    with (
        patch(_POST, return_value=answer),
        patch.object(CoreExceptionError, 'to_log') as to_log,
        pytest.raises(FourTochkiApiError) as raised,
    ):
        fetch_warehouses(_API)

    to_log.assert_called_once_with('method=GetWarehouses code=30 comment=Ошибка авторизации.')
    assert str(raised.value) == 'API Форточек вернул ошибку. Подробности в логе.'


def test_api_error_is_found_after_other_children() -> None:
    """error ищется среди всех дочерних элементов результата, а не только среди первых."""
    body = f'<a:success>false</a:success><a:other/>{_ERROR}'
    with (
        patch(_POST, return_value=_response('GetWarehouses', body)),
        patch.object(CoreExceptionError, 'to_log'),
        pytest.raises(FourTochkiApiError),
    ):
        fetch_warehouses(_API)


def test_error_without_comment_is_not_an_error() -> None:
    """error с пустым комментарием — успех: ответ разбирается дальше."""
    body = '<a:error><a:code>0</a:code><a:comment/></a:error><a:warehouses/>'
    with patch(_POST, return_value=_response('GetWarehouses', body)):
        assert fetch_warehouses(_API) == []


def test_missing_method_result_detail_names_method() -> None:
    """Нет элемента <…Result> — в лог идёт метод ответа."""
    with (
        patch(_POST, return_value=_response('GetFindDisk', '')),
        patch.object(CoreExceptionError, 'to_log') as to_log,
        pytest.raises(FourTochkiApiError),
    ):
        fetch_warehouses(_API)

    to_log.assert_called_once_with('API Форточек вернул ответ, который не удалось разобрать. method=GetWarehouses')


def test_unparsable_response_detail_has_message_and_parse_error() -> None:
    """Не-XML ответ: в лог идёт сообщение и ParseError, пользователю — сообщение об ошибке API."""
    with (
        patch(_POST, return_value=b'<html>502</html'),
        patch.object(CoreExceptionError, 'to_log') as to_log,
        pytest.raises(FourTochkiApiError),
    ):
        fetch_warehouses(_API)

    logged = to_log.call_args.args[0]
    assert logged.startswith('API Форточек вернул ответ, который не удалось разобрать.\nParseError(')


def test_connection_error_message_for_user() -> None:
    """Сообщение пользователю при сбое подключения — полный текст."""
    with (
        patch(_HTTPS, side_effect=OSError('down')),
        patch.object(CoreExceptionError, 'to_log'),
        pytest.raises(FourTochkiApiConnectionError) as raised,
    ):
        fetch_warehouses(_API)
    assert str(raised.value) == (
        'Не удалось подключиться к API Форточек. Проверьте интернет-соединение и параметры подключения.'
    )


_SEASON_CASES = [
    ('w', 'Зимняя'),
    ('s', 'Летняя'),
    ('u', 'Всесезонная'),
    ('x', ''),
    ('', ''),
    ('W', ''),
]
_SPIKE_CASES = [
    ('true', 'Да'),
    ('false', ''),
    ('', ''),
    ('TRUE', ''),
]
_DISK_TYPE_CASES = [
    ('0', 'Литой'),
    ('1', 'Штампованный'),
    ('2', 'Кованный'),
    ('9', ''),
    ('', ''),
]


@pytest.mark.parametrize(('season', 'expected'), _SEASON_CASES)
def test_tire_season_table(tmp_path: Path, season: str, expected: str) -> None:
    """Сезон API → слово прайса; неизвестный код и другой регистр дают пустую строку."""
    assert _tires(tmp_path, _tire(season=season))[0]['season'] == expected


@pytest.mark.parametrize(
    ('tire_type', 'expected'),
    [
        ('car', 'Легковая'),
        ('truck', 'Грузовая'),
        ('moto', 'Мото'),
        ('specteh', 'Спецтехника'),
        ('other', 'other'),
        ('', ''),
    ],
)
def test_tire_type_table(tmp_path: Path, tire_type: str, expected: str) -> None:
    """Тип шины: известный код → слово прайса, неизвестный остаётся как пришёл."""
    assert _tires(tmp_path, _tire(tire_type=tire_type))[0]['tire_type'] == expected


@pytest.mark.parametrize(('thorn', 'expected'), _SPIKE_CASES)
def test_tire_spike_flag(tmp_path: Path, thorn: str, expected: str) -> None:
    """Шип — только при точном 'true'."""
    assert _tires(tmp_path, _tire(thorn=thorn))[0]['spike'] == expected


@pytest.mark.parametrize(('disk_type', 'expected'), _DISK_TYPE_CASES)
def test_disk_type_table(tmp_path: Path, disk_type: str, expected: str) -> None:
    """Тип диска: неизвестный код — пустая строка."""
    assert _disks(tmp_path, _disk(disk_type=disk_type))[0]['disk_type'] == expected


def test_disk_row_has_exact_fields(tmp_path: Path) -> None:
    """Строка диска: все поля позиции и склада."""
    assert _disks(tmp_path, _disk()) == [
        {
            'code': '1',
            'title': 'N',
            'manufacturer_name': 'M',
            'model': 'Mod',
            'color': 'C',
            'disk_type': 'Литой',
            'price_opt': 10.0,
            'price_recommended': 20.0,
            'rest_count': 3,
            'warehouse_id': 7,
            'warehouse_name': 'Склад',
            'warehouse_group': None,
            'available': None,
            'delivery_period': None,
        },
    ]


def test_missing_numbers_default_to_zero(tmp_path: Path) -> None:
    """Пустые цена, остаток и склад дают 0 (склад 0 не настроен — строка пропущена), текст обрезается."""
    empty = '<b:wh_price_rest><b:price/><b:price_rozn> </b:price_rozn><b:rest/><b:wrh> 7 </b:wrh></b:wh_price_rest>'
    skipped = '<b:wh_price_rest><b:price>1</b:price><b:wrh/></b:wh_price_rest>'
    rows = _tires(tmp_path, _tire(whpr=empty + skipped))
    assert len(rows) == 1
    row = rows[0]
    assert row['price_opt'] == 0.0
    assert isinstance(row['price_opt'], float)
    assert row['price_recommended'] == 0.0
    assert row['rest_count'] == 0
    assert row['warehouse_id'] == 7


def test_responses_without_namespaces_are_parsed(tmp_path: Path) -> None:
    """Теги без пространства имён читаются так же, как с ним."""
    plain = (
        b'<Envelope><Body><GetFindTyreResponse><GetFindTyreResult><error/><price_rest_list>'
        b'<TyrePriceRest><code>5</code><marka>M</marka><model>X</model><name>T</name><season>s</season>'
        b'<thorn>false</thorn><type>moto</type><whpr><wh_price_rest><price>1.5</price><price_rozn>2</price_rozn>'
        b'<rest>4</rest><wrh>7</wrh></wh_price_rest></whpr></TyrePriceRest>'
        b'</price_rest_list><totalPages>1</totalPages></GetFindTyreResult></GetFindTyreResponse></Body></Envelope>'
    )
    tires = _download_pages(tmp_path, plain, _page('GetFindDisk'))[0]
    assert len(tires) == 1
    row = tires[0]
    assert (row['code'], row['season']) == ('5', 'Летняя')
    assert (row['price_opt'], row['rest_count']) == (1.5, 4)


def test_warehouse_directory_ignores_foreign_elements() -> None:
    """Справочник складов: берутся только WarehouseInfo, id и название обрезаются по краям."""
    body = (
        f'{_NIL_ERROR}<a:warehouses><a:Other><a:id>1</a:id><a:name>x</a:name></a:Other>'
        '<a:WarehouseInfo><a:id> 5 </a:id><a:name> Склад </a:name></a:WarehouseInfo>'
        '<a:WarehouseInfo><a:name>Без id</a:name></a:WarehouseInfo></a:warehouses>'
    )
    with patch(_POST, return_value=_response('GetWarehouses', body)):
        found = fetch_warehouses(_API)
    assert found == [
        FourTochkiApiWarehouse(id=5, name='Склад'),
        FourTochkiApiWarehouse(id=0, name='Без id'),
    ]


def test_download_creates_missing_parent_folders(tmp_path: Path) -> None:
    """Вложенная несуществующая папка создаётся целиком; существующая — не ошибка."""
    target = tmp_path / 'a' / 'b'
    for _ in range(2):
        with patch(_POST, side_effect=[_page('GetFindTyre'), _page('GetFindDisk')]):
            download_catalogs(dest_dir=target, api=_API, warehouses=(_WAREHOUSE,))
    assert json.loads((target / 'tire.json').read_text(encoding='utf-8')) == []


def test_rows_file_is_indented_utf8(tmp_path: Path) -> None:
    """Файл в UTF-8, кириллица не экранируется, отступ — два пробела."""
    _tires(tmp_path, _tire())
    text = (tmp_path / 'tire.json').read_text(encoding='utf-8')
    assert 'Склад' in text
    assert text.startswith('[\n  {\n    "code": "1"')


def test_unknown_warehouse_does_not_hide_following_ones(tmp_path: Path) -> None:
    """Склад вне настроек пропускается, а следующие за ним строки остаются."""
    foreign = _WHPR.replace('<b:wrh>7</b:wrh>', '<b:wrh>99</b:wrh>')
    rows = _tires(tmp_path, _tire(whpr=foreign + _WHPR))
    assert [row['warehouse_id'] for row in rows] == [7]
