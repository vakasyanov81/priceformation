"""Выбор источника данных поставщика: файлы или API из блока «api»."""

from typing import Any

import pytest

from domain.exceptions import ConfigValidationError
from parsers.vendor_config.models import VendorConfig
from parsers.vendor_config.source import select_source

_XLS_SECTION: dict[str, Any] = {
    'name': 'Файл',
    'columns': {'0': 'code'},
    'file_templates': ['price*.xlsx'],
}
_API_SECTION: dict[str, Any] = {
    'name': 'API',
    'file_templates': ['tire.json'],
    'columns': {'code': 'code'},
}


def _vendor(**extra: Any) -> dict[str, Any]:
    return {
        'enabled': 1,
        'code': '5',
        'name': 'Поставщик',
        'start_row': 2,
        'file_templates': ['price*.xlsx'],
        'sections': [_XLS_SECTION],
        'api': {'start_row': 0, 'reader': 'json', 'file_templates': ['tire.json'], 'sections': [_API_SECTION]},
        **extra,
    }


def test_file_source_is_default_and_drops_api_block() -> None:
    """Без поля source конфиг файлового источника; блок api не попадает в модель."""
    payload = select_source(_vendor(), 'vendor.json')
    assert 'api' not in payload
    assert 'source' not in payload
    assert payload['sections'] == [_XLS_SECTION]


def test_explicit_file_source_matches_default() -> None:
    """source: file даёт тот же конфиг, что и отсутствие поля."""
    assert select_source(_vendor(source='xlsx'), 'vendor.json') == select_source(_vendor(), 'vendor.json')


def test_api_source_replaces_top_level_with_api_block() -> None:
    """source: api берёт секции и reader из блока api; старые параметры файла не переносятся."""
    payload = select_source(_vendor(source='api'), 'vendor.json')
    assert payload['reader'] == 'json'
    assert payload['sections'] == [_API_SECTION]
    assert payload['file_templates'] == ['tire.json']
    assert payload['start_row'] == 0
    assert payload['enabled'] == 1
    assert payload['code'] == '5'


def test_api_source_builds_json_vendor_config() -> None:
    """Конфиг api проходит модель VendorConfig: reader json и секции из блока api."""
    config = VendorConfig.from_dict(select_source(_vendor(source='api'), 'vendor.json'), 'vendor', 'vendor.json')
    assert config.reader == 'json'
    assert [section.name for section in config.sections] == ['API']
    assert config.sections[0].columns == {'code': 'code'}


def test_unknown_source_is_error() -> None:
    """Неизвестный источник — ошибка конфига с именем файла."""
    with pytest.raises(ConfigValidationError, match='«source» должен быть «xlsx» или «api»'):
        select_source(_vendor(source='ftp'), 'vendor.json')


def test_api_source_without_block_is_error() -> None:
    """source: api без блока api — ошибка, а не пустой конфиг."""
    raw = _vendor(source='api')
    del raw['api']
    with pytest.raises(ConfigValidationError, match='нужен блок «api»'):
        select_source(raw, 'vendor.json')
