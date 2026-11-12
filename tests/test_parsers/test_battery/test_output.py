"""Аккумуляторные поля доходят до реальной записи без шинных преобразований."""

import json
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pytest
from openpyxl import load_workbook

from cfg.battery import make_battery_handler
from domain.battery.item import BatteryItem
from domain.battery.result import BatteryResult
from domain.product_groups import ProductGroup
from integration_tests.group_xlsx_examples import group_writer
from parsers.battery.output import BatteryOutputSource
from parsers.battery.output_fields import OUTPUT_FIELDS
from parsers.vendor_config.group_models import BatteryConfig
from parsers.vendor_config.models import VendorConfig
from parsers.writer.output_plan import prepare_output_plan
from parsers.writer.templates.group_output import GroupOutput
from parsers.writer.templates.tmpl.for_batteries import ForBatteries


def _source() -> BatteryOutputSource:
    position = BatteryItem.from_fields(
        {
            'title': 'XTREME Arctic 60',
            'code': '001',
            'price_opt': '4000.10',
            'price_recommended': '5500.20',
            'rest_count': 1,
            'efb': False,
        }
    )
    return BatteryOutputSource(BatteryResult((position,)))


def test_output_preserves_decimal_precision_codes_and_unknown_values() -> None:
    source = _source()
    group = ForBatteries().output_spec().groups[0]
    row = source.prepare('for_batteries', group)[0]
    assert row.keys() == OUTPUT_FIELDS
    assert row['price_opt'] == '4000.10'
    assert row['sale_price'] == row['price_recommended'] == '5500.20'
    assert row['code'] == '001'
    assert row['efb'] is False
    assert row['agm'] is None
    position = source.package.positions[0]
    assert position.offer.price_opt == Decimal('4000.10')


def test_output_filters_do_not_change_package() -> None:
    source = _source()
    group = ForBatteries().output_spec().groups[0]
    filtered = replace(group, filters={'is_main': [False]})
    assert source.prepare('for_batteries', filtered) == ()
    assert len(source.prepare('for_batteries', group)) == 1
    assert BatteryOutputSource(BatteryResult()).prepare('for_batteries', group) == ()


@pytest.mark.parametrize(
    'group, message',
    [
        (replace(ForBatteries().output_spec().groups[0], id=ProductGroup.TIRE_AND_DISK), 'другой группы'),
        (replace(ForBatteries().output_spec().groups[0], merge_warehouses=True), 'сведение складов'),
    ],
)
def test_output_rejects_inapplicable_rules(group: GroupOutput, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        _source().prepare('for_batteries', group)


def test_battery_template_writes_codes_prices_and_stock(tmp_path: Path) -> None:
    template = ForBatteries().output_spec()
    sources = {ProductGroup.BATTERIES: _source()}
    plan = prepare_output_plan([template], sources, current_date='2026-11-12')
    assert plan[0].sheets[0].title_fields == frozenset(('title',))
    paths = group_writer(tmp_path).write([template], sources, current_date='2026-11-12')
    workbook = load_workbook(paths[0])
    sheet = workbook['Аккумуляторы']
    header, cells = list(sheet.values)
    row = dict(zip(header, cells, strict=True))
    assert row['Код'] == '001'
    assert row['Цена продажи'] == row['РРЦ'] == '5500.20'
    assert row['Закупочная цена'] == '4000.10'
    assert row['Остаток'] == 1
    workbook.close()


def test_real_plant_settings_map_all_source_columns() -> None:
    path = Path('tests/parse_config_example/plant.json')
    raw = json.loads(path.read_text())
    config = VendorConfig.from_dict(raw, 'plant', str(path))
    group = config.product_groups[0]
    assert isinstance(group, BatteryConfig)
    section = group.sections[0]
    assert section.start_row == 6
    assert section.columns[21] == 'code'
    assert section.columns[24] == 'price_recommended'
    assert len(section.columns) == 24
    battery_handler = make_battery_handler(section, config.name)
    parsed = battery_handler.process_fields(
        [{'code': '001', 'title': 'XTREME +EFB 60', 'rest_count': '>30', 'price_recommended': '5000.10'}]
    )
    assert battery_handler.prepare_output(parsed)[0]['sale_price'] == '5000.10'
    for fixture in ('tasks/examples/plant.json', 'integration_tests/parse_config_example/plant.json'):
        assert json.loads(Path(fixture).read_text()) == raw
