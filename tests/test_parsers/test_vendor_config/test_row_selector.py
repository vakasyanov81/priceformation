"""Чтение и границы наследования селекторов строк."""

import pytest

from domain.exceptions import ConfigValidationError
from parsers.vendor_config.group_models import BatteryConfig, TireAndDiskConfig
from parsers.vendor_config.models import VendorConfig


def _config(group: dict[str, object], **vendor: object) -> VendorConfig:
    return VendorConfig.from_dict(
        {'code': 'demo', 'name': 'Поставщик', 'product_groups': [group], **vendor}, 'demo', 'demo.json'
    )


def _tire_group(section: dict[str, object]) -> dict[str, object]:
    return {
        'id': 'tire_and_disk',
        'file_templates': ['*.xlsx'],
        'columns': {'0': 'title'},
        'sections': [{'id': 'tires', **section}],
    }


def test_section_reads_exact_row_selector() -> None:
    raw_selector = {'column': '0', 'values': ['шина', ' Шина']}
    config = _config(_tire_group({'row_selector': raw_selector}))

    group = config.product_groups[0]
    assert isinstance(group, TireAndDiskConfig)
    selector = group.sections[0].row_selector
    assert selector is not None
    assert selector.column == '0'
    assert selector.accepted_values == ('шина', ' Шина')
    assert selector.matches({'0': ' Шина'})
    assert not selector.matches({'0': 'шина '})
    assert not selector.matches({'0': 1})
    assert not selector.matches({'0': ''})


def test_battery_route_has_selector_without_battery_fields() -> None:
    config = _config(
        {
            'id': 'batteries',
            'file_templates': ['*.xlsx'],
            'sections': [{'id': 'batteries', 'row_selector': {'column': 'kind', 'values': ['аккумулятор']}}],
        },
        reader='json',
    )

    group = config.product_groups[0]
    assert isinstance(group, BatteryConfig)
    assert group.sections[0].row_selector is not None


def test_row_selector_is_not_inherited_from_group() -> None:
    group = _tire_group({})
    group['row_selector'] = {'column': '0', 'values': ['шина']}

    with pytest.raises(ConfigValidationError, match=r'row_selector.*только в секции'):
        _config(group)


@pytest.mark.parametrize('raw_values', [[], ['шина', 'шина'], 'шина', [1]])
def test_invalid_selector_values_report_path(raw_values: object) -> None:
    with pytest.raises(ConfigValidationError, match=r'row_selector.*values|values.*row_selector'):
        _config(_tire_group({'row_selector': {'column': '0', 'values': raw_values}}))


def test_json_section_rejects_sheet_indexes() -> None:
    group = _tire_group({'sheet_indexes': [0]})
    group['columns'] = {'title': 'title'}

    with pytest.raises(ConfigValidationError, match='JSON не содержит листов'):
        _config(group, reader='json')
