"""Наследование групп: приоритеты, проверка источников и изоляция моделей."""

import json
from copy import deepcopy
from pathlib import Path

import pytest

from domain.exceptions import ConfigValidationError
from infrastructure.config.fake_config_provider import FakeConfigProvider
from parsers.data_provider.json_fields import RawConfig
from parsers.vendor_config.common import CommonVendorSettings
from parsers.vendor_config.group_models import BatteryConfig, TireAndDiskConfig
from parsers.vendor_config.models import VendorConfig
from parsers.vendor_config.provider import load_vendor_configs


def _vendor() -> RawConfig:
    return {
        'code': 'demo',
        'name': 'Поставщик',
        'defaults': {'start_row': 3},
        'product_groups': [
            {
                'id': 'tire_and_disk',
                'start_row': 4,
                'sections': [{'id': 'tires', 'start_row': 5}],
            },
            {'id': 'batteries', 'sections': [{'id': 'batteries'}]},
        ],
    }


def _common() -> RawConfig:
    return {
        'defaults': {'start_row': 1, 'file_templates': ['*.xlsx']},
        'product_groups': [
            {
                'id': 'tire_and_disk',
                'defaults': {
                    'start_row': 2,
                    'columns': {'0': 'title'},
                    'title': {'params_from_title': True},
                    'behavior': {'min_rest': 9},
                },
            }
        ],
        'title_reference_order': ['demo'],
    }


def _load(payload: RawConfig, common: RawConfig) -> VendorConfig:
    settings = CommonVendorSettings.from_dict(common, '_common.json')
    return VendorConfig.from_dict(payload, 'demo', 'demo.json', common=settings)


@pytest.mark.parametrize('level', range(5))
def test_reading_settings_follow_five_levels(level: int) -> None:
    common = _common()
    vendor = _vendor()
    group = vendor['product_groups'][0]
    levels = [
        common['defaults'],
        common['product_groups'][0]['defaults'],
        vendor['defaults'],
        group,
        group['sections'][0],
    ]
    for index, settings in enumerate(levels):
        settings['file_templates'] = [f'{index}.xlsx']
        if index > level:
            settings.pop('start_row')
            settings.pop('file_templates')

    section = _load(vendor, common).sections[0]

    assert section.start_row == level + 1
    assert section.file_templates == (f'{level}.xlsx',)


def test_common_settings_do_not_leak_between_groups() -> None:
    config = _load(_vendor(), _common())
    tires, batteries = config.product_groups

    assert isinstance(tires, TireAndDiskConfig)
    assert isinstance(batteries, BatteryConfig)
    assert tires.sections[0].columns == {0: 'title'}
    assert tires.sections[0].title.params_from_title is True
    assert tires.sections[0].behavior.min_rest == 9
    assert batteries.sections[0].start_row == 3
    assert batteries.sections[0].file_templates == ('*.xlsx',)
    assert not hasattr(batteries.sections[0], 'columns')
    assert not hasattr(batteries.sections[0], 'behavior')


def test_model_settings_merge_only_inside_own_group() -> None:
    vendor = _vendor()
    group = vendor['product_groups'][0]
    group['columns'] = {'1': 'code'}
    group['title'] = {'params_first': True}
    group['sections'] = [
        {
            'id': 'first',
            'columns': {'2': 'rest_count'},
            'title': {'params_from_title': False},
            'behavior': {'min_rest': 0},
        },
        {'id': 'second', 'title': {}},
    ]

    first, second = _load(vendor, _common()).sections

    assert first.columns == {2: 'rest_count'}
    assert first.title.params_from_title is False
    assert first.title.params_first is True
    assert first.behavior.min_rest == 0
    assert second.columns == {1: 'code'}
    assert second.title.params_from_title is True
    assert second.behavior.min_rest == 9


def test_common_groups_do_not_declare_vendor_groups() -> None:
    vendor = _vendor()
    vendor['product_groups'].pop(0)

    config = _load(vendor, _common())

    assert len(config.product_groups) == 1
    assert isinstance(config.product_groups[0], BatteryConfig)
    assert not config.sections


@pytest.mark.parametrize('key', ['columns', 'file_templates'])
def test_empty_final_settings_are_not_restored(key: str) -> None:
    vendor = _vendor()
    group = vendor['product_groups'][0]
    group['sections'][0][key] = {} if key == 'columns' else []

    with pytest.raises(ConfigValidationError, match=key):
        _load(vendor, _common())


@pytest.mark.parametrize('level', range(5))
@pytest.mark.parametrize('key, invalid', [('start_row', None), ('file_templates', 3)])
def test_invalid_reading_level_cannot_be_hidden(level: int, key: str, invalid: object) -> None:
    common = _common()
    vendor = _vendor()
    group = vendor['product_groups'][0]
    levels = [
        common['defaults'],
        common['product_groups'][0]['defaults'],
        vendor['defaults'],
        group,
        group['sections'][0],
    ]
    levels[level][key] = invalid
    expected_file = '_common.json' if level < 2 else 'demo.json'

    with pytest.raises(ConfigValidationError) as caught:
        _load(vendor, common)

    assert expected_file in str(caught.value)
    assert key in str(caught.value)


@pytest.mark.parametrize('level', ['common', 'group', 'section'])
@pytest.mark.parametrize('key', ['columns', 'title', 'pricing', 'category', 'behavior'])
def test_invalid_model_level_cannot_be_hidden(level: str, key: str) -> None:
    common = _common()
    vendor = _vendor()
    group = vendor['product_groups'][0]
    section = group['sections'][0]
    section[key] = {'0': 'title'} if key == 'columns' else {}
    common_defaults = common['product_groups'][0]['defaults']
    levels = {'common': common_defaults, 'group': group, 'section': section}
    levels[level][key] = None

    with pytest.raises(ConfigValidationError) as caught:
        _load(vendor, common)

    message = str(caught.value)
    expected_file = '_common.json' if level == 'common' else 'demo.json'
    assert expected_file in message
    assert 'product_groups[0]' in message
    assert key in message


@pytest.mark.parametrize('key', ['columns', 'title', 'pricing', 'category', 'behavior'])
def test_common_reading_defaults_reject_model_settings(key: str) -> None:
    common = _common()
    common['defaults'][key] = {}

    with pytest.raises(ConfigValidationError, match=f'defaults → {key}'):
        _load(_vendor(), common)


@pytest.mark.parametrize('groups', [None, {}, [None], [{'id': 'unknown'}]])
def test_invalid_common_groups_report_source(groups: object) -> None:
    with pytest.raises(ConfigValidationError, match=r'_common\.json → product_groups'):
        CommonVendorSettings.from_dict({'product_groups': groups}, '_common.json')


def test_common_duplicate_groups_report_both_paths() -> None:
    groups = [{'id': 'tire_and_disk'}, {'id': 'tire_and_disk'}]
    with pytest.raises(ConfigValidationError) as caught:
        CommonVendorSettings.from_dict({'product_groups': groups}, '_common.json')

    assert 'product_groups[0].id' in str(caught.value)
    assert 'product_groups[1].id' in str(caught.value)


@pytest.mark.parametrize('key', ['sections', 'sheet_indexes', 'id', 'name', 'product_groups'])
def test_common_group_defaults_cannot_define_routes(key: str) -> None:
    common = _common()
    common['product_groups'][0]['defaults'][key] = []

    with pytest.raises(ConfigValidationError, match=f'defaults → {key}'):
        _load(_vendor(), common)


def test_common_group_cannot_define_sections() -> None:
    common = _common()
    common['product_groups'][0]['sections'] = [{'id': 'implicit'}]

    with pytest.raises(ConfigValidationError, match=r'product_groups\[0\] → sections'):
        _load(_vendor(), common)


def test_common_battery_defaults_cannot_contain_tire_slots() -> None:
    common = {'product_groups': [{'id': 'batteries', 'defaults': {'title': {}}}]}

    with pytest.raises(ConfigValidationError, match=r'_common\.json.*defaults → title'):
        _load(_vendor(), common)


def test_group_inheritance_through_file_provider(fake_config_provider: FakeConfigProvider) -> None:
    directory = Path(fake_config_provider.config_file('vendors'))
    directory.mkdir(parents=True, exist_ok=True)
    directory.joinpath('_common.json').write_text(json.dumps(_common()), encoding='utf-8')
    directory.joinpath('demo.json').write_text(json.dumps(_vendor()), encoding='utf-8')

    config = load_vendor_configs(fake_config_provider)['demo']

    assert config.sections[0].title.params_from_title is True
    assert config.sections[0].start_row == 5
    assert len(config.product_groups) == 2


def test_new_common_settings_support_legacy_vendor() -> None:
    vendor = {'code': 'old', 'name': 'Старый', 'sections': [{'id': 'old'}]}

    config = _load(vendor, _common())

    assert config.sections[0].columns == {0: 'title'}
    assert config.sections[0].start_row == 2
    assert config.behavior.min_rest == 9


def test_resolved_sections_and_sources_are_independent() -> None:
    common = _common()
    defaults = common['product_groups'][0]['defaults']
    defaults['category'] = {'map': {'raw': 'Шины'}}
    vendor = _vendor()
    group = vendor['product_groups'][0]
    group['sections'] = [{'id': 'first'}, {'id': 'second'}]
    original_common, original_vendor = deepcopy(common), deepcopy(vendor)
    first, second = _load(vendor, common).sections

    first.category.mapping['raw'] = 'Диски'
    first.columns[1] = 'code'

    assert second.category.mapping == {'raw': 'Шины'}
    assert second.columns == {0: 'title'}
    assert common == original_common
    assert vendor == original_vendor


def test_battery_defaults_are_applied_only_to_batteries() -> None:
    common = _common()
    common['product_groups'].append({'id': 'batteries', 'defaults': {'file_templates': ['batteries.xlsx']}})

    config = _load(_vendor(), common)
    batteries = config.product_groups[1]

    assert isinstance(batteries, BatteryConfig)
    assert batteries.sections[0].file_templates == ('batteries.xlsx',)
    assert config.sections[0].file_templates == ('*.xlsx',)


def test_common_column_keys_are_validated_for_vendor_reader() -> None:
    common = _common()
    common['product_groups'][0]['defaults']['columns'] = {'article': 'code'}
    vendor = _vendor()
    vendor['product_groups'][0]['columns'] = {'1': 'title'}

    with pytest.raises(ConfigValidationError, match=r'_common\.json.*defaults.*article'):
        _load(vendor, common)

    vendor['reader'] = 'json'
    assert _load(vendor, common).sections[0].columns == {'1': 'title'}


@pytest.mark.parametrize('extra', [{}, {'product_groups': []}])
def test_shared_reading_defaults_need_no_group_declarations(extra: RawConfig) -> None:
    common = {'defaults': {'file_templates': ['common.xlsx']}, **extra}
    vendor = _vendor()
    vendor['product_groups'][0]['columns'] = {'0': 'title'}

    config = _load(vendor, common)

    assert config.sections[0].file_templates == ('common.xlsx',)


def test_markup_rules_replace_through_all_model_levels() -> None:
    common = _common()
    common['product_groups'][0]['defaults']['pricing'] = {
        'rules': {'markup_rules': {'common': {'min': 0, 'max': 10, 'percent': 0.1}}}
    }
    vendor = _vendor()
    group = vendor['product_groups'][0]
    vendor_rules = {'vendor': {'min': 10, 'max': 20, 'percent': 0.2}}
    group['pricing'] = {'rules': {'markup_rules': vendor_rules}}
    empty_section = {'id': 'empty', 'pricing': {'rules': {'markup_rules': {}}}}
    group['sections'] = [empty_section, {'id': 'inherited'}]

    empty, inherited = _load(vendor, common).sections

    assert not empty.pricing.rules.markup_rules
    assert list(inherited.pricing.rules.markup_rules) == ['vendor']
