"""tests for black list and vendor list providers"""

from unittest.mock import patch

import pytest

from domain.exceptions import ConfigValidationError, CoreExceptionError
from parsers.data_provider import VendorConfigEntry
from parsers.data_provider.black_list import BlackListProviderBase, BlackListProviderFromUserConfig
from parsers.data_provider.vendor_list import (
    VendorListConfigFileError,
    VendorListProviderBase,
    VendorListProviderFromUserConfig,
)

_TO_LOG = 'to_log'
_VENDOR_LIST_FILE = 'vendor_list.json'


def test_black_list_base_raises() -> None:
    with pytest.raises(NotImplementedError):
        BlackListProviderBase().get_black_list_data()


def test_black_list_masks_base_raises() -> None:
    with pytest.raises(NotImplementedError):
        BlackListProviderBase().get_stop_words_data()


def test_black_list_from_config() -> None:
    with patch('parsers.data_provider.black_list.read_file', return_value='a\nb\n'):
        provider = BlackListProviderFromUserConfig()
        assert provider.get_black_list_data() == ['a', 'b']
        assert provider.get_stop_words_data() == []


def test_black_list_from_config_splits_masks() -> None:
    raw = 'exact title\n*некондиция*\n*2 сорт*\n'
    with patch('parsers.data_provider.black_list.read_file', return_value=raw):
        provider = BlackListProviderFromUserConfig()
        assert provider.get_black_list_data() == ['exact title']
        assert provider.get_stop_words_data() == ['*некондиция*', '*2 сорт*']


def test_vendor_list_base_raises() -> None:
    with pytest.raises(NotImplementedError):
        VendorListProviderBase().get_config_vendor_list()


def test_vendor_list_file_missing() -> None:
    with (
        patch.object(CoreExceptionError, _TO_LOG),
        patch(
            'infrastructure.data.file_reader.read_file',
            side_effect=FileNotFoundError,
        ),
        pytest.raises(VendorListConfigFileError),
    ):
        VendorListProviderFromUserConfig().get_config_vendor_list()


def test_vendor_list_parsed_into_models() -> None:
    raw = '{"stk": {"enabled": 0}, "mim": {"enabled": 1}}'
    with patch('infrastructure.data.file_reader.read_file', return_value=raw):
        vendors = VendorListProviderFromUserConfig().get_config_vendor_list()

    assert vendors == {
        'stk': VendorConfigEntry(enabled=False),
        'mim': VendorConfigEntry(enabled=True),
    }


def test_vendor_list_bad_enabled_reports_file_and_vendor() -> None:
    raw = '{"stk": {"enabled": 2}}'
    with (
        patch.object(ConfigValidationError, _TO_LOG),
        patch('infrastructure.data.file_reader.read_file', return_value=raw),
        pytest.raises(ConfigValidationError) as exc_info,
    ):
        VendorListProviderFromUserConfig().get_config_vendor_list()
    message = str(exc_info.value)
    assert f'{_VENDOR_LIST_FILE} → stk' in message
    assert '«enabled» должен быть 0 или 1' in message


def test_vendor_list_entry_must_be_object() -> None:
    with (
        patch.object(ConfigValidationError, _TO_LOG),
        patch('infrastructure.data.file_reader.read_file', return_value='{"stk": 1}'),
        pytest.raises(ConfigValidationError, match='ожидается объект'),
    ):
        VendorListProviderFromUserConfig().get_config_vendor_list()


def test_vendor_list_broken_json_reports_file() -> None:
    with (
        patch.object(ConfigValidationError, _TO_LOG),
        patch('infrastructure.data.file_reader.read_file', return_value='{"stk":'),
        pytest.raises(ConfigValidationError, match='не удалось разобрать JSON') as exc_info,
    ):
        VendorListProviderFromUserConfig().get_config_vendor_list()
    assert _VENDOR_LIST_FILE in str(exc_info.value)
