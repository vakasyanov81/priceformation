"""HTTPS client for MIM catalog download."""

import gzip
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from domain.exceptions import CoreExceptionError
from infrastructure.config.fake_config_provider import FakeConfigProvider
from parsers.remote.mim_client import (
    MimApiConnectionError,
    MimApiRequest,
    MimApiResponseError,
    MimApiTypesError,
    download_catalog,
    get_catalog,
    get_territories,
    load_remote_vendor_data,
    resolve_types,
)

_TEST_SECRET = 'secret'
_TEST_HOST = 'api.test'
_TO_LOG = 'to_log'
_HTTPS = 'parsers.remote.mim_client.HTTPSConnection'
_API = MimApiRequest(host=_TEST_HOST, token=_TEST_SECRET, types=(1, 3, 4))
_XML = 'PK-xlsx-тест'.encode()


def test_get_catalog_sends_token_and_format() -> None:
    mock_https = _https_mock(body=_XML)

    with patch(_HTTPS, mock_https):
        body = get_catalog(_API)

    assert mock_https.call_args.args == (_TEST_HOST,)
    method, url = mock_https.return_value.request.call_args.args
    assert method == 'GET'
    assert url == '/api/v1/catalog/unload?access-token=secret&format=xlsx&gzip=true&types=1%3B3%3B4'
    mock_https.return_value.close.assert_called_once()
    assert body == _XML


def test_get_catalog_unpacks_gzip() -> None:
    with patch(_HTTPS, _https_mock(body=gzip.compress(_XML))):
        assert get_catalog(_API) == _XML


def test_get_territories_sends_token() -> None:
    mock_https = _https_mock(body=b'[]')

    with patch(_HTTPS, mock_https):
        body = get_territories(_API)

    assert mock_https.return_value.request.call_args.args == ('GET', '/goods/unload/territories-list?token=secret')
    assert body == b'[]'


def test_get_territories_bad_status_hides_token() -> None:
    with (
        patch(_HTTPS, _https_mock(body=b'denied', status=403)),
        patch.object(CoreExceptionError, _TO_LOG) as mock_log,
        pytest.raises(MimApiResponseError),
    ):
        get_territories(_API)

    logged = mock_log.call_args.args[0]
    assert 'territories-list' in logged
    assert _TEST_SECRET not in logged


def test_get_catalog_connection_error_hides_token() -> None:
    mock_https = _https_mock(error=OSError('network down'))

    with (
        patch(_HTTPS, mock_https),
        patch.object(CoreExceptionError, _TO_LOG) as mock_log,
        pytest.raises(MimApiConnectionError, match='Не удалось подключиться') as raised,
    ):
        get_catalog(_API)

    logged = mock_log.call_args.args[0]
    assert 'network down' in logged
    assert _TEST_HOST in logged
    assert _TEST_SECRET not in logged
    assert _TEST_SECRET not in str(raised.value)


def test_get_catalog_bad_status_hides_token() -> None:
    mock_https = _https_mock(body=b'denied', status=401)

    with (
        patch(_HTTPS, mock_https),
        patch.object(CoreExceptionError, _TO_LOG) as mock_log,
        pytest.raises(MimApiResponseError, match='MIM_API_TOKEN'),
    ):
        get_catalog(_API)

    logged = mock_log.call_args.args[0]
    assert 'status=401' in logged
    assert _TEST_SECRET not in logged


def test_download_catalog_writes_file_and_overwrites(tmp_path: Path) -> None:
    dest = tmp_path / 'nested' / 'mim'

    with (
        patch('parsers.remote.mim_client.get_catalog', side_effect=[b'old-xlsx', _XML]),
        patch('parsers.remote.mim_client.get_territories', side_effect=[b'[1]', b'[2]']),
    ):
        download_catalog(dest_dir=dest, api=_API)
        download_catalog(dest_dir=dest, api=_API)

    assert (dest / 'price.xlsx').read_bytes() == _XML
    assert (dest / 'territories.json').read_bytes() == b'[2]'


def test_download_catalog_keeps_old_file_on_error(tmp_path: Path) -> None:
    dest = tmp_path / 'mim'
    dest.mkdir()
    (dest / 'price.xlsx').write_bytes(b'old')

    with (
        patch('parsers.remote.mim_client.get_catalog', return_value=_XML),
        patch('parsers.remote.mim_client.get_territories', side_effect=MimApiResponseError(detail='x')),
        pytest.raises(MimApiResponseError),
    ):
        download_catalog(dest_dir=dest, api=_API)

    assert (dest / 'price.xlsx').read_bytes() == b'old'
    assert not (dest / 'territories.json').exists()


def test_load_remote_vendor_data_uses_config_provider(fake_config_provider: FakeConfigProvider) -> None:
    with patch('parsers.remote.mim_client.download_catalog') as mock_download:
        load_remote_vendor_data(api=_API)

    mock_download.assert_called_once_with(dest_dir=Path(fake_config_provider.price_folder('mim')), api=_API)


def _https_mock(*, body: bytes | None = None, status: int = 200, error: Exception | None = None) -> MagicMock:
    mock_cls = MagicMock()
    connection = mock_cls.return_value
    if error is None:
        response = connection.getresponse.return_value
        response.status = status
        response.read.return_value = body
    else:
        connection.request.side_effect = error
    return mock_cls


_TYPES_CASES = [
    ((), (1, 3, 4)),
    ((2,), (2,)),
    ((4, 3, 4, 7), (4, 3, 7)),
]


@pytest.mark.parametrize(('configured', 'expected'), _TYPES_CASES)
def test_resolve_types(configured: tuple[int, ...], expected: tuple[int, ...]) -> None:
    assert resolve_types(configured) == expected


@pytest.mark.parametrize('configured', [(0,), (8,), (1, -1)])
def test_resolve_types_unknown(configured: tuple[int, ...]) -> None:
    with patch.object(CoreExceptionError, _TO_LOG), pytest.raises(MimApiTypesError, match='неверные категории'):
        resolve_types(configured)
