"""SOAP-клиент Форточек: разбор ответов, постраничность, ошибки и запись JSON."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from domain.exceptions import CoreExceptionError
from infrastructure.config.fake_config_provider import FakeConfigProvider
from infrastructure.config.four_tochki_api_config import FourTochkiApiConfig
from parsers.remote.four_tochki_client import (
    FourTochkiApiConnectionError,
    FourTochkiApiError,
    download_catalogs,
    load_remote_vendor_data,
)

_API = FourTochkiApiConfig(endpoint='https://api.test/WCF/ClientService.svc', login='a&b', password='secret')
_POST = 'parsers.remote.four_tochki_client._post'
_HTTPS = 'parsers.remote.four_tochki_client.HTTPSConnection'
_TO_LOG = 'to_log'
_NS_RESULT = 'xmlns:a="x" xmlns:b="y" xmlns:i="z"'
_TIRE_POSITION = (
    '<a:TyrePriceRest>'
    '<a:code>3151006</a:code><a:marka>Viatti</a:marka><a:model>Brina</a:model>'
    '<a:name>185/70R14 88T Brina TL (94 шип.)</a:name>'
    '<a:season>w</a:season><a:thorn>true</a:thorn><a:type>car</a:type>'
    '<a:whpr>'
    '<b:wh_price_rest><b:price>4394</b:price><b:price_rozn>5544</b:price_rozn><b:rest>1</b:rest><b:wrh>1423</b:wrh>'
    '</b:wh_price_rest>'
    '<b:wh_price_rest><b:price>4400</b:price><b:price_rozn>5600</b:price_rozn><b:rest>41</b:rest><b:wrh>2167</b:wrh>'
    '</b:wh_price_rest>'
    '</a:whpr>'
    '</a:TyrePriceRest>'
)
_DISK_POSITION = (
    '<a:DiskPriceRest>'
    '<a:code>WHS502222</a:code><a:color>GMF</a:color><a:marka>Replay</a:marka><a:model>FA21</a:model>'
    '<a:name>7x17/5x114,3 ET40 D57,1 FA21 GMF</a:name><a:type>0</a:type>'
    '<a:whpr><b:wh_price_rest><b:price>8000</b:price><b:price_rozn>8000</b:price_rozn>'
    '<b:rest>1</b:rest><b:wrh>1423</b:wrh></b:wh_price_rest></a:whpr>'
    '</a:DiskPriceRest>'
)


def _soap(method: str, positions: str = '', total_pages: int = 1, error: str = '') -> bytes:
    """Ответ SOAP с одной страницей поиска."""
    error_xml = error or '<a:error i:nil="true"/>'
    return (
        '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body>'
        f'<{method}Response xmlns="Wcf.ClientService.Client.WebAPI.TS3">'
        f'<{method}Result {_NS_RESULT}>'
        f'<a:currencyRate><b:charCode>RUB</b:charCode></a:currencyRate>'
        f'{error_xml}'
        f'<a:price_rest_list>{positions}</a:price_rest_list>'
        f'<a:totalPages>{total_pages}</a:totalPages>'
        f'</{method}Result></{method}Response></s:Body></s:Envelope>'
    ).encode()


def test_download_writes_rows_per_warehouse(tmp_path: Path) -> None:
    """Шина с двумя складами даёт две строки; сезон, шип и тип диска приведены к словарю прайса."""
    responses = [
        _soap('GetFindTyre', _TIRE_POSITION),
        _soap('GetFindDisk', _DISK_POSITION),
    ]
    with patch(_POST, side_effect=responses):
        download_catalogs(dest_dir=tmp_path, api=_API)

    tires = json.loads((tmp_path / 'tire.json').read_text(encoding='utf-8'))
    disks = json.loads((tmp_path / 'disk.json').read_text(encoding='utf-8'))
    assert len(tires) == 2
    assert tires[0] == {
        'code': '3151006',
        'title': '185/70R14 88T Brina TL (94 шип.)',
        'manufacturer_name': 'Viatti',
        'model': 'Brina',
        'season': 'Зимняя',
        'spike': 'Да',
        'tire_type': 'Легковая',
        'price_opt': 4394.0,
        'price_recommended': 5544.0,
        'rest_count': 1,
        'warehouse_id': 1423,
    }
    assert tires[1]['rest_count'] == 41
    assert tires[1]['warehouse_id'] == 2167
    assert len(disks) == 1
    assert disks[0]['disk_type'] == 'Литой'
    assert disks[0]['color'] == 'GMF'
    assert disks[0]['price_opt'] == 8000.0


def test_pages_are_requested_until_total(tmp_path: Path) -> None:
    """Постраничный обход: страницы запрашиваются, пока не будет totalPages."""
    responses = [
        _soap('GetFindTyre', _TIRE_POSITION, total_pages=2),
        _soap('GetFindTyre', _TIRE_POSITION, total_pages=2),
        _soap('GetFindDisk', '', total_pages=0),
    ]
    with patch(_POST, side_effect=responses) as mock_post:
        download_catalogs(dest_dir=tmp_path, api=_API)

    envelopes = [call.args[2] for call in mock_post.call_args_list]
    tyre_envelopes = [envelope for envelope in envelopes if b'GetFindTyre' in envelope]
    assert len(tyre_envelopes) == 2
    assert b'<page>0</page>' in tyre_envelopes[0]
    assert b'<page>1</page>' in tyre_envelopes[1]
    assert mock_post.call_count == 3
    tires = json.loads((tmp_path / 'tire.json').read_text(encoding='utf-8'))
    assert len(tires) == 4


def test_login_is_escaped_in_request(tmp_path: Path) -> None:
    """Спецсимволы логина экранируются в XML запроса."""
    responses = [_soap('GetFindTyre'), _soap('GetFindDisk')]
    with patch(_POST, side_effect=responses) as mock_post:
        download_catalogs(dest_dir=tmp_path, api=_API)
    assert b'<login>a&amp;b</login>' in mock_post.call_args_list[0].args[2]


def test_request_targets_endpoint_with_soap_action(tmp_path: Path) -> None:
    """Запрос уходит на адрес сервиса с заголовком SOAPAction метода."""
    connection = MagicMock()
    connection.getresponse.return_value.read.side_effect = [_soap('GetFindTyre'), _soap('GetFindDisk')]
    with patch(_HTTPS, return_value=connection) as mock_https:
        download_catalogs(dest_dir=tmp_path, api=_API)

    mock_https.assert_called_with('api.test')
    first_request = connection.request.call_args_list[0]
    assert first_request.args[:2] == ('POST', '/WCF/ClientService.svc')
    soap_action = first_request.kwargs['headers']['SOAPAction']
    assert soap_action == '"Wcf.ClientService.Client.WebAPI.TS3/ClientService/GetFindTyre"'


def test_response_without_method_result_raises(tmp_path: Path) -> None:
    """Ответ без элемента ожидаемого метода — ошибка API, а не падение итератора."""
    with (
        patch(_POST, return_value=_soap('GetFindDisk')),
        patch.object(CoreExceptionError, _TO_LOG),
        pytest.raises(FourTochkiApiError, match='вернул ошибку'),
    ):
        download_catalogs(dest_dir=tmp_path, api=_API)


def test_api_error_comment_raises(tmp_path: Path) -> None:
    """error с комментарием — ошибка API, файлы не пишутся."""
    error = '<a:error><a:code>30</a:code><a:comment>Ошибка авторизации.</a:comment></a:error>'
    with (
        patch(_POST, return_value=_soap('GetFindTyre', error=error)),
        patch.object(CoreExceptionError, _TO_LOG),
        pytest.raises(FourTochkiApiError),
    ):
        download_catalogs(dest_dir=tmp_path, api=_API)
    assert not (tmp_path / 'tire.json').exists()


def test_unparsable_response_raises(tmp_path: Path) -> None:
    """Ответ, который не XML, — ошибка API."""
    with (
        patch(_POST, return_value=b'<html>502</html'),
        patch.object(CoreExceptionError, _TO_LOG),
        pytest.raises(FourTochkiApiError),
    ):
        download_catalogs(dest_dir=tmp_path, api=_API)


def test_connection_error_raises(tmp_path: Path) -> None:
    """Сетевой сбой превращается в ошибку подключения."""
    with (
        patch(_HTTPS, side_effect=OSError('network down')),
        patch.object(CoreExceptionError, _TO_LOG),
        pytest.raises(FourTochkiApiConnectionError, match='Не удалось подключиться'),
    ):
        download_catalogs(dest_dir=tmp_path, api=_API)


def test_load_remote_vendor_data_uses_price_folder(fake_config_provider: FakeConfigProvider) -> None:
    """Данные кладутся в папку прайсов Форточек из конфигурации путей."""
    with patch(_POST, side_effect=[_soap('GetFindTyre'), _soap('GetFindDisk')]):
        load_remote_vendor_data(api=_API)

    folder = Path(fake_config_provider.price_folder('four_tochki'))
    assert json.loads((folder / 'tire.json').read_text(encoding='utf-8')) == []
    assert json.loads((folder / 'disk.json').read_text(encoding='utf-8')) == []


def test_filters_are_sent_in_contract_namespace_with_novosibirsk_warehouses(tmp_path: Path) -> None:
    """Поля фильтра в пространстве имён контракта; склады — только Новосибирск (1423 и ОХ)."""
    responses = [_soap('GetFindTyre'), _soap('GetFindDisk')]
    with patch(_POST, side_effect=responses) as mock_post:
        download_catalogs(dest_dir=tmp_path, api=_API)

    tyre_envelope, disk_envelope = (call.args[2] for call in mock_post.call_args_list)
    tyre_ns = b'SearchTires"'
    disk_ns = b'SearchDiscs"'
    assert tyre_ns in tyre_envelope
    assert (
        b'<wrh_list xmlns="http://schemas.datacontract.org/2004/07/TS3.Domain.Models.Client.ClientSoapService.SearchTires">'
        in tyre_envelope
    )
    assert b'<int xmlns="http://schemas.microsoft.com/2003/10/Serialization/Arrays">1423</int>' in tyre_envelope
    assert b'<include_paid_delivery xmlns=' in tyre_envelope
    assert disk_ns in disk_envelope
    assert b'<rim_vid_name_list xmlns=' in disk_envelope
    assert b'<string xmlns="http://schemas.microsoft.com/2003/10/Serialization/Arrays">truck</string>' in disk_envelope
