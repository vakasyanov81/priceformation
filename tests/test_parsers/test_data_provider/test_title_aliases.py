"""tests for title aliases provider"""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from infrastructure.config.fake_config_provider import FakeConfigProvider
from parsers.data_provider.title_aliases import (
    TitleAliasesProviderBase,
    TitleAliasesProviderFromUserConfig,
    invert_title_aliases,
    load_title_aliases,
)
from parsers.vendors import zapaska_disk_json

_ALIASES_FILE = 'title_aliases.json'
_DISK_SUPPLIER = 'Запаска (диски)'
_TIRE_SUPPLIER = 'Запаска (шины)'
_ALIASES_JSON = json.dumps(
    {
        _DISK_SUPPLIER: {'Replay Honda': ['Replay HND']},
        _TIRE_SUPPLIER: {'Three-A': ['THREE-A']},
    }
)


def test_title_aliases_base_raises() -> None:
    with pytest.raises(NotImplementedError):
        TitleAliasesProviderBase().get_aliases()


def test_invert_title_aliases() -> None:
    assert invert_title_aliases({'Good': ['Bad', 'Worse']}) == {'Bad': 'Good', 'Worse': 'Good'}


def test_load_title_aliases_missing_file() -> None:
    with patch('parsers.data_provider.title_aliases.read_file', side_effect=FileNotFoundError):
        assert load_title_aliases(_DISK_SUPPLIER) == {}


def test_load_aliases_inverts_supplier_section(fake_config_provider: FakeConfigProvider) -> None:
    with patch('parsers.data_provider.title_aliases.read_file', return_value=_ALIASES_JSON) as mock_read:
        assert load_title_aliases(_DISK_SUPPLIER) == {'Replay HND': 'Replay Honda'}
        assert load_title_aliases(_TIRE_SUPPLIER) == {'THREE-A': 'Three-A'}
        assert load_title_aliases('unknown') == {}
        mock_read.assert_called_with(fake_config_provider.config_file(_ALIASES_FILE))


def test_load_title_aliases_from_real_file(fake_config_provider: FakeConfigProvider) -> None:
    config_file = Path(fake_config_provider.config_file(_ALIASES_FILE))
    config_file.write_text(_ALIASES_JSON, encoding='utf-8')
    assert load_title_aliases(_DISK_SUPPLIER) == {'Replay HND': 'Replay Honda'}


def test_provider_reads_config_file(fake_config_provider: FakeConfigProvider) -> None:
    with patch('parsers.data_provider.title_aliases.read_file', return_value='{}') as mock_read:
        assert TitleAliasesProviderFromUserConfig(_DISK_SUPPLIER).get_aliases() == {}
        mock_read.assert_called_once_with(fake_config_provider.config_file(_ALIASES_FILE))


def test_zapaska_disk_json_does_not_import_cfg() -> None:
    source = Path(zapaska_disk_json.__file__).read_text(encoding='utf-8')
    assert 'from cfg' not in source
    assert 'import cfg' not in source
