"""Загрузка конфигов поставщиков из parse_config/vendors с кэшем."""

import json
from pathlib import Path

import pytest

from domain.exceptions import ConfigValidationError
from infrastructure.config.fake_config_provider import FakeConfigProvider
from parsers.vendor_config.activation import set_vendor_enabled
from parsers.vendor_config.provider import (
    clear_vendor_configs_cache,
    load_vendor_configs,
)

FOLDER = 'vendors'
ACTIVATION_FILE = 'vendor_activation.json'
MIM_JSON = (
    '{"code": "mim", "name": "Мим", "start_row": 2, '
    '"file_templates": ["*.xls"], "sections": [{"columns": {"1": "manufacturer_name"}}]}'
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


def _activation_path(provider: FakeConfigProvider) -> Path:
    return Path(provider.config_file(ACTIVATION_FILE))


def _read_activation(provider: FakeConfigProvider) -> dict[str, int]:
    statuses: dict[str, int] = json.loads(_activation_path(provider).read_text(encoding='utf-8'))
    return statuses


def test_missing_activation_file_keeps_vendors_enabled(fake_config_provider: FakeConfigProvider) -> None:
    """Без vendor_activation.json все поставщики включены."""
    _vendors_dir(fake_config_provider).joinpath('mim.json').write_text(MIM_JSON, encoding='utf-8')

    assert load_vendor_configs()['mim'].enabled is True


def test_activation_file_sets_status(fake_config_provider: FakeConfigProvider) -> None:
    """Статус берётся из vendor_activation.json по имени папки."""
    _vendors_dir(fake_config_provider).joinpath('mim.json').write_text(MIM_JSON, encoding='utf-8')
    _activation_path(fake_config_provider).write_text('{"mim": 0}', encoding='utf-8')
    clear_vendor_configs_cache()

    assert load_vendor_configs()['mim'].enabled is False


def test_set_vendor_enabled_writes_activation_file(fake_config_provider: FakeConfigProvider) -> None:
    """Переключение пишет статус в vendor_activation.json, сам конфиг поставщика не трогает."""
    path = _vendors_dir(fake_config_provider).joinpath('mim.json')
    path.write_text(MIM_JSON, encoding='utf-8')
    assert load_vendor_configs()['mim'].enabled is True

    set_vendor_enabled('mim', False)

    assert _read_activation(fake_config_provider) == {'mim': 0}
    assert path.read_text(encoding='utf-8') == MIM_JSON
    assert load_vendor_configs()['mim'].enabled is False


def test_set_vendor_enabled_keeps_other_vendors(fake_config_provider: FakeConfigProvider) -> None:
    """Запись одного поставщика не трогает статусы остальных."""
    _activation_path(fake_config_provider).write_text('{"stk": 0, "mim": 1}', encoding='utf-8')

    set_vendor_enabled('mim', False)

    assert _read_activation(fake_config_provider) == {'mim': 0, 'stk': 0}


def test_activation_file_rejects_bad_flag(fake_config_provider: FakeConfigProvider) -> None:
    """Статус только 0 или 1; ошибка называет файл активации."""
    _activation_path(fake_config_provider).write_text('{"mim": 2}', encoding='utf-8')
    _vendors_dir(fake_config_provider).joinpath('mim.json').write_text(MIM_JSON, encoding='utf-8')

    with pytest.raises(ConfigValidationError, match=r'vendor_activation\.json'):
        load_vendor_configs()


def test_enabled_in_vendor_json_is_rejected(fake_config_provider: FakeConfigProvider) -> None:
    """Поле enabled в конфиге поставщика больше не действует — ошибка с подсказкой, куда его перенесли."""
    source = MIM_JSON.replace('"code"', '"enabled": 1, "code"', 1)
    _vendors_dir(fake_config_provider).joinpath('mim.json').write_text(source, encoding='utf-8')

    with pytest.raises(ConfigValidationError, match=r'mim\.json: «enabled» перенесён в vendor_activation\.json'):
        load_vendor_configs()


def test_common_defaults_apply_to_every_vendor(fake_config_provider: FakeConfigProvider) -> None:
    """Общие настройки `_common.json` действуют у поставщика, пока он не задал своё значение."""
    folder = _vendors_dir(fake_config_provider)
    folder.joinpath('_common.json').write_text(
        '{"defaults": {"start_row": 7, "behavior": {"min_rest": 0}, "title": {"params_from_title": true}}}',
        encoding='utf-8',
    )
    folder.joinpath('mim.json').write_text(MIM_JSON, encoding='utf-8')

    config = load_vendor_configs()['mim']

    assert set(load_vendor_configs()) == {'mim'}
    assert config.sections[0].start_row == 2
    assert config.behavior.min_rest == 0
    assert config.sections[0].title.params_from_title is True


def test_common_file_errors_name_file(fake_config_provider: FakeConfigProvider) -> None:
    folder = _vendors_dir(fake_config_provider)
    folder.joinpath('_common.json').write_text('{"defaults": []}', encoding='utf-8')
    folder.joinpath('mim.json').write_text(MIM_JSON, encoding='utf-8')

    with pytest.raises(ConfigValidationError, match=r'_common\.json → defaults: ожидается объект'):
        load_vendor_configs()
