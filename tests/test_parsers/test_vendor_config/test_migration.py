"""Переход конфигов сохраняет разрешённые настройки и требует решения коллизий."""

import json
from copy import deepcopy
from pathlib import Path

import pytest

from domain.exceptions import ConfigValidationError
from parsers.vendor_config.common import CommonVendorSettings
from parsers.vendor_config.migration import migrate_common_config, migrate_vendor_config, migrate_vendor_sources
from parsers.vendor_config.models import VendorConfig
from parsers.vendor_config.source import select_source

_EXAMPLE_FOLDERS = ('tests/parse_config_example/vendors', 'integration_tests/parse_config_example/vendors')
_VENDORS = ('autosnab54_ru', 'four_tochki', 'mim', 'pioner', 'poshk', 'stk', 'zapaska')


@pytest.mark.parametrize('directory', _EXAMPLE_FOLDERS)
@pytest.mark.parametrize('folder', _VENDORS)
def test_example_sources_preserve_settings(directory: str, folder: str) -> None:
    """Файловый и API-вариант каждого эталона переносятся независимо."""
    raw = json.loads(Path(directory, f'{folder}.json').read_text(encoding='utf-8'))
    for source in ('xlsx', 'api') if 'api' in raw else ('xlsx',):
        selected = select_source({**raw, 'source': source}, f'{folder}.json')
        original = deepcopy(selected)
        before = VendorConfig.from_dict(selected, folder, f'{folder}.json')
        assert before.configured_groups
        section_count = len(before.sections)
        identifiers = tuple(f'{folder}_{index}' for index in range(section_count))
        migrated = migrate_vendor_config(
            selected,
            folder,
            f'{folder}.json',
            section_ids=None if before.configured_groups else identifiers,
        )
        after = VendorConfig.from_dict(migrated, folder, f'{folder}.json')
        assert selected == original
        assert after.reader == before.reader
        assert after.source == before.source
        assert after.behavior == before.behavior
        for old_section, new_section in zip(before.sections, after.sections, strict=True):
            assert new_section.columns == old_section.columns
            assert new_section.title == old_section.title
            assert new_section.category == old_section.category
            assert new_section.pricing == old_section.pricing
            assert new_section.file_templates == old_section.file_templates
            assert new_section.start_row == old_section.start_row
            assert new_section.sheet_indexes == old_section.sheet_indexes
            assert new_section.behavior == old_section.behavior
        assert migrate_vendor_config(migrated, folder, f'{folder}.json') == migrated


def _legacy() -> dict[str, object]:
    return {
        'code': 'demo',
        'name': 'Поставщик',
        'columns': {'0': 'title'},
        'file_templates': ['*.xlsx'],
        'sections': [{}],
    }


def test_legacy_sections_inherit_behavior_before_migration() -> None:
    """Общее поведение доходит до секций, которые переопределяют отдельные параметры."""
    common = CommonVendorSettings.from_dict(
        {'defaults': {'behavior': {'manufacturer_column_first': True, 'min_rest': 7}}},
        '_common.json',
    )
    raw = {
        **_legacy(),
        'behavior': {'min_rest': 0},
        'sections': [{'id': 'first'}, {'id': 'second', 'behavior': {'min_rest': 2}}],
    }
    before = VendorConfig.from_dict(raw, 'demo', 'demo.json', common=common)
    first, second = before.sections
    assert first.behavior.min_rest == 0
    assert second.behavior.min_rest == 2
    assert first.behavior.manufacturer_column_first
    assert second.behavior.manufacturer_column_first
    migrated = migrate_vendor_config(raw, 'demo', 'demo.json', common=common)
    after_common = CommonVendorSettings.from_dict(migrate_common_config({'defaults': common.defaults}), '_common.json')
    after = VendorConfig.from_dict(migrated, 'demo', 'demo.json', common=after_common)
    assert after.sections == before.sections


@pytest.mark.parametrize('source', ['xlsx', 'api'])
def test_complete_vendor_preserves_both_sources(source: str) -> None:
    """Полный перенос сохраняет альтернативный источник, слоты и выбранный режим."""
    raw = {
        **_legacy(),
        'source': source,
        'title': {'params_from_title': True},
        'api': {
            'reader': 'json',
            'title': {'params_first': True},
            'sections': [{'columns': {'name': 'title'}, 'file_templates': ['tire.json']}],
        },
    }
    original = deepcopy(raw)
    migrated = migrate_vendor_sources(raw, 'demo', 'demo.json')
    assert raw == original
    assert migrated['source'] == source
    for selected_source in ('xlsx', 'api'):
        before = VendorConfig.from_dict(
            select_source({**raw, 'source': selected_source}, 'demo.json'),
            'demo',
            'demo.json',
        )
        after = VendorConfig.from_dict(
            select_source({**migrated, 'source': selected_source}, 'demo.json'),
            'demo',
            'demo.json',
        )
        assert after.sections == before.sections
    assert migrate_vendor_sources(migrated, 'demo', 'demo.json') == migrated


def test_complete_vendor_without_api_preserves_source_absence() -> None:
    """У файлового поставщика не появляются служебные source и api."""
    migrated = migrate_vendor_sources(_legacy(), 'demo', 'demo.json')
    assert 'source' not in migrated
    assert 'api' not in migrated


@pytest.mark.parametrize('common_already_migrated', [False, True])
def test_common_defaults_preserve_inheritance(common_already_migrated: bool) -> None:
    raw = {
        'title_reference_order': ['demo'],
        'defaults': {'start_row': 3, 'title': {'params_from_title': True}, 'behavior': {'min_rest': 7}},
    }
    original = deepcopy(raw)
    common = CommonVendorSettings.from_dict(raw, '_common.json')
    migrated = migrate_common_config(raw)
    after_common = CommonVendorSettings.from_dict(migrated, '_common.json')
    if common_already_migrated:
        common = after_common
    payload = migrate_vendor_config(_legacy(), 'demo', 'demo.json', common=common)
    before = VendorConfig.from_dict(_legacy(), 'demo', 'demo.json', common=common)
    after = VendorConfig.from_dict(payload, 'demo', 'demo.json', common=after_common)
    assert raw == original
    assert after.sections[0].id == before.sections[0].id
    assert after.sections[0].title == before.sections[0].title
    assert after.sections[0].start_row == before.sections[0].start_row
    assert after.sections[0].behavior == before.sections[0].behavior
    assert after.behavior == before.behavior
    assert after_common.title_reference_order == common.title_reference_order
    assert migrated['defaults'] == {'start_row': 3}
    assert migrate_common_config(migrated) == migrated


_INVALID_IDS = (None, ('same', 'same'), ('only_one',), ('', 'other'))


@pytest.mark.parametrize('identifiers', _INVALID_IDS)
def test_ambiguous_section_ids_require_explicit_resolution(identifiers: tuple[str, ...] | None) -> None:
    payload = {**_legacy(), 'sections': [{}, {}]}
    with pytest.raises(ConfigValidationError, match=r'demo.json.*sections'):
        migrate_vendor_config(payload, 'demo', 'demo.json', section_ids=identifiers)


@pytest.mark.parametrize('extra', [{'api': {}}, {'defaults': {}}])
def test_unselected_or_mixed_config_rejected(extra: dict[str, object]) -> None:
    with pytest.raises(ConfigValidationError, match=r'demo\.json'):
        migrate_vendor_config({**_legacy(), **extra}, 'demo', 'demo.json')


def test_unknown_common_default_rejected() -> None:
    with pytest.raises(ConfigValidationError, match='defaults → unknown'):
        migrate_common_config({'defaults': {'unknown': True}})


def test_migrated_ids_cannot_be_reassigned() -> None:
    migrated = migrate_vendor_config(_legacy(), 'demo', 'demo.json')
    with pytest.raises(ConfigValidationError, match='section_ids'):
        migrate_vendor_config(migrated, 'demo', 'demo.json', section_ids=('other',))
