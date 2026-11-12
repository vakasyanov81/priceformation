"""Типизированные объявления групп и совместимость старого формата."""

import json
from pathlib import Path

import pytest

from domain.exceptions import ConfigValidationError
from domain.product_groups import ProductGroup
from infrastructure.config.fake_config_provider import FakeConfigProvider
from parsers.registry import all_vendors_from_registry, vendor_entry_for
from parsers.vendor_config.group_models import BatteryConfig, TireAndDiskConfig
from parsers.vendor_config.models import VendorConfig
from parsers.vendor_config.provider import load_vendor_configs
from parsers.vendor_config.section_models import VendorSection


def test_section_group_does_not_depend_on_name() -> None:
    """Отображаемое имя и описание листа не меняют модель настроек секции."""
    section = VendorSection(
        id='demo', name='Аккумуляторы', start_row=1, file_templates=('*.xlsx',), columns={0: 'title'}
    )

    assert section.product_group is ProductGroup.TIRE_AND_DISK


def _grouped_config(groups: object, **overrides: object) -> VendorConfig:
    return VendorConfig.from_dict(
        {'code': 'demo', 'name': 'Поставщик', 'product_groups': groups, **overrides}, 'demo', 'demo.json'
    )


def _tire_group() -> dict[str, object]:
    return {
        'id': 'tire_and_disk',
        'file_templates': ['tires*.xlsx'],
        'columns': {'0': 'title'},
        'behavior': {'min_rest': 9},
        'sections': [{'id': 'tires'}],
    }


def _battery_group() -> dict[str, object]:
    return {'id': 'batteries', 'file_templates': ['batteries*.xlsx'], 'sections': [{'id': 'batteries'}]}


def test_two_groups_have_separate_settings() -> None:
    config = _grouped_config([_tire_group(), _battery_group()], defaults={'start_row': 3})

    tires, batteries = config.product_groups
    assert isinstance(tires, TireAndDiskConfig)
    assert isinstance(batteries, BatteryConfig)
    assert tires.sections == config.sections
    assert tires.behavior.min_rest == 9
    assert batteries.id is ProductGroup.BATTERIES
    section = batteries.sections[0]
    assert section.product_group is ProductGroup.BATTERIES
    assert section.id == 'batteries'
    assert section.start_row == 3
    assert section.file_templates == ('batteries*.xlsx',)
    assert not hasattr(section, 'columns')


def test_battery_only_config_has_no_tire_sections() -> None:
    config = _grouped_config([_battery_group()])

    assert config.sections == ()
    assert len(config.product_groups) == 1
    assert config.product_groups[0].id is ProductGroup.BATTERIES


@pytest.mark.parametrize('groups', [None, [], {}, 'tire_and_disk', [None]])
def test_invalid_group_structure_reports_path(groups: object) -> None:
    with pytest.raises(ConfigValidationError, match=r'demo\.json → product_groups'):
        _grouped_config(groups)


@pytest.mark.parametrize('identifier', [None, '', 'Tire_And_Disk', ' tire_and_disk', 'unknown'])
def test_invalid_group_identifier_reports_path(identifier: object) -> None:
    with pytest.raises(ConfigValidationError, match=r'product_groups\[0\].id'):
        _grouped_config([{'id': identifier, 'sections': [{'id': 'demo'}]}])


def test_duplicate_group_reports_both_paths() -> None:
    with pytest.raises(ConfigValidationError) as caught:
        _grouped_config([_tire_group(), _tire_group()])

    assert 'product_groups[0].id' in str(caught.value)
    assert 'product_groups[1].id' in str(caught.value)


@pytest.mark.parametrize('sections', [None, [], {}, [None]])
def test_invalid_group_sections_rejected(sections: object) -> None:
    group = {**_tire_group(), 'sections': sections}
    with pytest.raises(ConfigValidationError, match=r'product_groups\[0\] → sections'):
        _grouped_config([group])


@pytest.mark.parametrize(
    'key', ['columns', 'sections', 'category', 'title', 'pricing', 'behavior', 'start_row', 'file_templates']
)
def test_mixed_legacy_and_grouped_format_rejected(key: str) -> None:
    with pytest.raises(ConfigValidationError, match='нельзя сочетать'):
        _grouped_config([_tire_group()], **{key: {}})


def test_group_section_requires_explicit_id() -> None:
    group = {**_tire_group(), 'sections': [{}]}
    with pytest.raises(ConfigValidationError, match=r'sections\[0\].id'):
        _grouped_config([group])


def test_section_cannot_override_group_membership() -> None:
    group = {**_tire_group(), 'sections': [{'id': 'demo', 'product_group': 'batteries'}]}
    with pytest.raises(ConfigValidationError, match='группа определяется вложенностью'):
        _grouped_config([group])


@pytest.mark.parametrize('key', ['columns', 'category', 'title', 'pricing', 'behavior'])
def test_batteries_cannot_use_tire_settings(key: str) -> None:
    group = {**_battery_group(), key: {}}
    with pytest.raises(ConfigValidationError, match='ещё не определены'):
        _grouped_config([group])


def test_group_defaults_cannot_contain_tire_settings() -> None:
    with pytest.raises(ConfigValidationError, match='defaults → columns'):
        _grouped_config([_tire_group()], defaults={'columns': {'0': 'title'}})


def test_battery_requires_file_templates() -> None:
    with pytest.raises(ConfigValidationError, match='file_templates'):
        _grouped_config([{'id': 'batteries', 'sections': [{'id': 'demo'}]}])


def test_grouped_vendor_rejects_unknown_reader() -> None:
    with pytest.raises(ConfigValidationError, match='reader'):
        _grouped_config([_tire_group()], reader='csv')


def _write_grouped_vendor(provider: FakeConfigProvider, folder: str, groups: list[dict[str, object]]) -> None:
    directory = Path(provider.config_file('vendors'))
    directory.mkdir(exist_ok=True, parents=True)
    payload = {'code': folder, 'name': folder, 'product_groups': groups}
    directory.joinpath(f'{folder}.json').write_text(json.dumps(payload), encoding='utf-8')


@pytest.mark.parametrize('disabled', [False, True])
def test_section_id_unique_across_disabled_vendors(fake_config_provider: FakeConfigProvider, disabled: bool) -> None:
    _write_grouped_vendor(fake_config_provider, 'first', [_tire_group()])
    _write_grouped_vendor(fake_config_provider, 'second', [_tire_group()])
    Path(fake_config_provider.config_file('vendor_activation.json')).write_text(
        json.dumps({'second': int(not disabled)}), encoding='utf-8'
    )

    with pytest.raises(ConfigValidationError) as caught:
        load_vendor_configs(fake_config_provider)

    message = str(caught.value)
    assert 'first.json → product_groups[0].sections[0].id (tire_and_disk)' in message
    assert 'second.json → product_groups[0].sections[0].id (tire_and_disk)' in message


def test_section_id_unique_across_groups(fake_config_provider: FakeConfigProvider) -> None:
    battery = {**_battery_group(), 'sections': [{'id': 'tires'}]}
    _write_grouped_vendor(fake_config_provider, 'demo', [_tire_group(), battery])

    with pytest.raises(ConfigValidationError) as caught:
        load_vendor_configs(fake_config_provider)

    assert 'product_groups[0].sections[0].id (tire_and_disk)' in str(caught.value)
    assert 'product_groups[1].sections[0].id (batteries)' in str(caught.value)


def test_battery_preflight_rejects_all_but_allows_tire_selection(fake_config_provider: FakeConfigProvider) -> None:
    _write_grouped_vendor(fake_config_provider, 'demo', [_tire_group(), _battery_group()])

    config = load_vendor_configs(fake_config_provider)['demo']
    assert len(config.product_groups) == 2
    assert vendor_entry_for('tires', fake_config_provider)[1].vendor_section == config.sections[0]
    with pytest.raises(ConfigValidationError, match=r'demo\.json.*batteries'):
        all_vendors_from_registry(fake_config_provider)
    with pytest.raises(ConfigValidationError, match=r'demo\.json.*batteries'):
        vendor_entry_for('batteries', fake_config_provider)


def test_grouped_vendor_rejects_unmigrated_common_defaults(fake_config_provider: FakeConfigProvider) -> None:
    _write_grouped_vendor(fake_config_provider, 'demo', [_tire_group()])
    Path(fake_config_provider.config_file('vendors/_common.json')).write_text(
        json.dumps({'defaults': {'behavior': {'min_rest': 5}}}), encoding='utf-8'
    )

    with pytest.raises(ConfigValidationError, match=r'_common\.json'):
        load_vendor_configs(fake_config_provider)


@pytest.mark.parametrize(
    ('slot', 'key', 'strategy_name'),
    [
        ('category', 'strategy', 'tire_compose'),
        ('title', 'strategy', 'fixed'),
        ('pricing', 'policy', 'unknown'),
        ('behavior', 'rest', 'unknown'),
        ('behavior', 'pipeline', ['unknown']),
    ],
)
@pytest.mark.parametrize('in_section', [False, True])
def test_strategy_names_checked_at_loading(slot: str, key: str, strategy_name: object, in_section: bool) -> None:
    """Чужое имя отклоняется загрузчиком, включая секционное переопределение."""
    group = _tire_group()
    settings = {slot: {key: strategy_name}}
    if in_section:
        group['sections'] = [{'id': 'tires', **settings}]
    else:
        group.update(settings)
    with pytest.raises(ConfigValidationError) as caught:
        _grouped_config([group])
    message = str(caught.value)
    assert 'demo.json → product_groups[0]' in message
    assert f'{slot} → {key}' in message
    assert ('sections[0]' in message) is in_section


def test_overridden_invalid_strategy_still_rejected() -> None:
    """Позднее переопределение не скрывает ошибку исходного уровня."""
    group = {**_tire_group(), 'title': {'strategy': 'unknown'}}
    group['sections'] = [{'id': 'tires', 'title': {'strategy': 'default'}}]
    with pytest.raises(ConfigValidationError, match='title → strategy'):
        _grouped_config([group])
