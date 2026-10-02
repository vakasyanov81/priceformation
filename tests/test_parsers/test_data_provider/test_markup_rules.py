"""tests for markup rules provider"""

from unittest.mock import patch

import pytest

from domain.exceptions import ConfigValidationError, CoreExceptionError
from infrastructure.config.fake_config_provider import FakeConfigProvider
from parsers.data_provider import MarkupRulesConfig
from parsers.data_provider.markup_rules import (
    MarkupRulesProviderBase,
    MarkupRulesProviderFromUserConfig,
    PriceRulesConfigFileError,
)

_TO_LOG = 'to_log'
_MISSING_FILE = '/no'
_STK_RULES_FILE = 'stk_markup_rules.json'
_MARKUP_RULES_FILE = 'markup_rules.json'
_MISSING_MSG = r'Filed to read vendor \(stk\) settings'


def test_markup_rules_base() -> None:
    provider = MarkupRulesProviderBase('s1')
    assert provider.supplier_name == 's1'
    with pytest.raises(NotImplementedError):
        provider.get_markup_data()


def test_markup_path_with_supplier(fake_config_provider: FakeConfigProvider) -> None:
    provider = MarkupRulesProviderFromUserConfig('stk')
    assert provider.get_file_path() == fake_config_provider.config_file(_STK_RULES_FILE)


def test_markup_path_default(fake_config_provider: FakeConfigProvider) -> None:
    provider = MarkupRulesProviderFromUserConfig()
    assert provider.get_file_path() == fake_config_provider.config_file(_MARKUP_RULES_FILE)


def test_markup_missing_file() -> None:
    provider = MarkupRulesProviderFromUserConfig('stk')
    with (
        patch.object(CoreExceptionError, _TO_LOG),
        patch.object(provider, 'get_file_path', return_value=_MISSING_FILE),
        patch(
            'infrastructure.data.file_reader.read_file',
            side_effect=FileNotFoundError,
        ) as mock_read,
        pytest.raises(PriceRulesConfigFileError, match=_MISSING_MSG),
    ):
        provider.get_markup_data()
    mock_read.assert_called_once_with(_MISSING_FILE)


def test_load_markup_broken_json_reports_file() -> None:
    provider = MarkupRulesProviderFromUserConfig('stk')
    with (
        patch.object(ConfigValidationError, _TO_LOG),
        patch('infrastructure.data.file_reader.read_file', return_value='{'),
        pytest.raises(ConfigValidationError, match='не удалось разобрать JSON') as exc_info,
    ):
        provider.get_markup_data()
    assert _STK_RULES_FILE in str(exc_info.value)


def test_load_markup_reads_file_path(fake_config_provider: FakeConfigProvider) -> None:
    provider = MarkupRulesProviderFromUserConfig('stk')
    rules_path = fake_config_provider.config_file(_STK_RULES_FILE)
    with patch('infrastructure.data.file_reader.read_file', return_value='{}') as mock_read:
        assert provider.get_markup_data() == MarkupRulesConfig()
        mock_read.assert_called_once_with(rules_path)


def test_broken_markup_json_reports_file_and_key(
    fake_config_provider: FakeConfigProvider,
) -> None:
    provider = MarkupRulesProviderFromUserConfig('stk')
    raw = '{"markup_rules": {"r": {"min": "abc"}}}'
    with (
        patch.object(ConfigValidationError, _TO_LOG),
        patch('infrastructure.data.file_reader.read_file', return_value=raw),
        pytest.raises(ConfigValidationError) as exc_info,
    ):
        provider.get_markup_data()
    message = str(exc_info.value)
    assert f'{_STK_RULES_FILE} → markup_rules.r' in message
    assert '«min» должно быть числом' in message


def test_markup_root_must_be_object() -> None:
    provider = MarkupRulesProviderFromUserConfig('stk')
    with (
        patch.object(ConfigValidationError, _TO_LOG),
        patch('infrastructure.data.file_reader.read_file', return_value='[]'),
        pytest.raises(ConfigValidationError, match='ожидается объект'),
    ):
        provider.get_markup_data()
