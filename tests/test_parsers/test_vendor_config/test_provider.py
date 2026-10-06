"""Загрузка конфигов поставщиков из parse_config/vendors с кэшем."""

from pathlib import Path

import pytest

from domain.exceptions import ConfigValidationError
from infrastructure.config.fake_config_provider import FakeConfigProvider
from parsers.vendor_config.provider import clear_vendor_configs_cache, load_vendor_configs

FOLDER = 'vendors'
MIM_JSON = (
    '{"enabled": 1, "code": "mim", "name": "Мим", "start_row": 2, '
    '"file_templates": ["*.xls"], "sections": [{"columns": {"1": "Бренд"}}]}'
)


def _vendors_dir(provider: FakeConfigProvider) -> Path:
    folder = Path(provider.config_file(FOLDER))
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def test_missing_folder_gives_empty_mapping(fake_config_provider: FakeConfigProvider) -> None:
    assert load_vendor_configs() == {}


def test_configs_keyed_by_file_stem(fake_config_provider: FakeConfigProvider) -> None:
    _vendors_dir(fake_config_provider).joinpath('mim.json').write_text(MIM_JSON, encoding='utf-8')

    configs = load_vendor_configs()

    assert set(configs) == {'mim'}
    assert configs['mim'].code == 'mim'


def test_broken_json_reports_file_name(fake_config_provider: FakeConfigProvider) -> None:
    _vendors_dir(fake_config_provider).joinpath('bad.json').write_text('{', encoding='utf-8')

    with pytest.raises(ConfigValidationError, match=r'bad\.json'):
        load_vendor_configs()


def test_invalid_config_reports_file_name(fake_config_provider: FakeConfigProvider) -> None:
    _vendors_dir(fake_config_provider).joinpath('mim.json').write_text('{"enabled": 0}', encoding='utf-8')

    with pytest.raises(ConfigValidationError, match=r'mim\.json'):
        load_vendor_configs()


def test_result_is_cached_until_cleared(fake_config_provider: FakeConfigProvider) -> None:
    folder = _vendors_dir(fake_config_provider)
    assert load_vendor_configs() == {}

    folder.joinpath('mim.json').write_text(MIM_JSON, encoding='utf-8')
    assert load_vendor_configs() == {}

    clear_vendor_configs_cache()
    assert set(load_vendor_configs()) == {'mim'}
