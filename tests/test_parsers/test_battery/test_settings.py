"""Собственные поля, стратегии и наследование аккумуляторной группы."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from openpyxl import Workbook

from cfg.battery import make_battery_handler
from domain.exceptions import ConfigValidationError
from parsers.base_parser.base_parser_config import ParseParamsSupplier, ParserParams
from parsers.base_parser.file_reader import FileReader
from parsers.base_parser.routing import VendorRouting
from parsers.base_parser.routing_rows import map_row
from parsers.data_provider.json_fields import RawConfig
from parsers.raw_table import RawRow
from parsers.vendor_config.battery_settings import BatterySettings
from parsers.vendor_config.common import CommonVendorSettings
from parsers.vendor_config.group_models import BatteryConfig, BatterySection
from parsers.vendor_config.models import VendorConfig


def _config(group: RawConfig, *, reader: str = 'xls', common: RawConfig | None = None) -> VendorConfig:
    return VendorConfig.from_dict(
        {
            'code': 'plant',
            'name': 'План-Т',
            'reader': reader,
            'product_groups': [
                {'id': 'batteries', 'file_templates': ['*.xls'], 'sections': [{'id': 'plant_battery'}], **group}
            ],
        },
        'plant',
        'plant.json',
        common=CommonVendorSettings.from_dict(common or {}, '_common.json'),
    )


def _section(config: VendorConfig) -> BatterySection:
    group = config.product_groups[0]
    assert isinstance(group, BatteryConfig)
    return group.sections[0]


COLUMN_EXAMPLES = [('xls', {'0': 'capacity_ah'}), ('json', ['capacity_ah'])]


@pytest.mark.parametrize('reader, columns', COLUMN_EXAMPLES)
def test_battery_columns_use_own_registry(reader: str, columns: object) -> None:
    section = _section(_config({'columns': columns}, reader=reader))
    expected_key = 0 if reader == 'xls' else 'capacity_ah'
    assert section.columns == {expected_key: 'capacity_ah'}
    assert section.processing.min_rest == 1


MARKUP_EXAMPLES = [(0.2, '6000'), (0.35, '6750'), (0, '5000')]


@pytest.mark.parametrize('percent, expected', MARKUP_EXAMPLES)
@pytest.mark.parametrize('recommended', [5000, 4900])
def test_markup_comes_from_pricing_rules(percent: float, expected: str, recommended: int) -> None:
    section = _section(
        _config(
            {
                'columns': {'0': 'code', '1': 'title', '2': 'rest_count', '3': 'price_recommended'},
                'pricing': {'rules': {'markup_rules': [{'min': 0, 'max': 999999999, 'percent': percent}]}},
            }
        )
    )
    battery_handler = make_battery_handler(section, 'plant')
    parsed = battery_handler.process_fields(
        [
            {
                'code': '001',
                'title': 'XTREME Arctic',
                'rest_count': 1,
                'price_opt': 5000,
                'price_recommended': recommended,
            }
        ]
    )
    assert battery_handler.prepare_output(parsed)[0]['sale_price'] == expected


@pytest.mark.parametrize(
    'setting, path',
    [
        ({'columns': {'0': 'season'}}, 'columns'),
        ({'category': {}}, 'category'),
        ({'title': {'strategy': 'default'}}, 'title → strategy'),
        ({'title': {'compose': True}}, 'title → compose'),
        ({'pricing': {'policy': 'base'}}, 'pricing → policy'),
        ({'behavior': {'rest': 'unknown'}}, 'behavior → rest'),
        ({'behavior': {'min_rest': 0}}, 'behavior → min_rest'),
        ({'behavior': {'pipeline': ['markup']}}, 'behavior → pipeline'),
        ({'title': {'lines': []}}, 'title → lines'),
        ({'title': {'lines': ['  ']}}, 'title → lines'),
        ({'title': {'lines': ['XTREME', 'xtreme']}}, 'title → lines'),
    ],
)
def test_invalid_battery_setting_has_source_and_slot(setting: RawConfig, path: str) -> None:
    with pytest.raises(ConfigValidationError) as caught:
        _config(setting)
    assert 'plant.json → product_groups[0]' in str(caught.value)
    assert path in str(caught.value)


def test_section_settings_inherit_without_sharing_columns() -> None:
    common: RawConfig = {
        'product_groups': [
            {
                'id': 'batteries',
                'defaults': {
                    'columns': {'0': 'code'},
                    'behavior': {'min_rest': 2},
                    'title': {'lines': ['  XTREME   Arctic  ']},
                },
            },
        ]
    }
    sections = [
        {'id': 'first'},
        {'id': 'second', 'columns': {'1': 'title'}, 'behavior': {'min_rest': 1}},
    ]
    config = _config({'sections': sections}, common=common)
    group = config.product_groups[0]
    assert isinstance(group, BatteryConfig)
    first, second = group.sections
    assert first.columns == {0: 'code'}
    assert second.columns == {1: 'title'}
    assert first.processing == BatterySettings(lines=('XTREME Arctic',), min_rest=2)
    assert second.processing == BatterySettings(lines=('XTREME Arctic',), min_rest=1)
    defaults = common['product_groups'][0]['defaults']
    assert defaults['title']['lines'] == ['  XTREME   Arctic  ']


def test_invalid_common_strategy_cannot_be_hidden_by_override() -> None:
    common = {'product_groups': [{'id': 'batteries', 'defaults': {'title': {'strategy': 'default'}}}]}
    with pytest.raises(ConfigValidationError, match=r'_common\.json.*title → strategy'):
        _config({'title': {'strategy': 'plant'}}, common=common)


def test_factory_requires_mapped_publication_fields_before_reading() -> None:
    section = _section(_config({'columns': {'0': 'title'}}))
    with pytest.raises(ConfigValidationError, match=r'plant.json.*sections\[0\].*columns.*price_recommended'):
        make_battery_handler(section, 'plant')


def test_json_mapping_feeds_factory_and_preserves_supplier_code() -> None:
    settings = {'columns': ['title', 'code', 'rest_count', 'price_recommended']}
    section = _section(_config(settings, reader='json'))
    config = _config({}, reader='json')
    parser_params = ParserParams(
        supplier=ParseParamsSupplier('plant', 'План-Т', 'plant_battery'),
        columns=dict(section.columns),
        start_row=1,
        sheet_info='',
        stop_words=(),
        file_templates=('*.json',),
        sheet_indexes=(),
    )
    fields = map_row(
        config,
        RawRow({'title': 'XTREME Arctic', 'code': '001', 'rest_count': 1, 'price_recommended': '5500.10'}, 1),
        parser_params,
    )
    battery_handler = make_battery_handler(section, 'plant')
    parsed = battery_handler.process([battery_handler.create_position(fields)])
    assert parsed.positions[0].identity.code == '001'
    assert parsed.positions[0].identity.model == 'XTREME Arctic'


def test_xlsx_routing_maps_battery_fields_before_creating_positions(tmp_path: Path) -> None:
    path = tmp_path / 'battery.xlsx'
    workbook = Workbook()
    sheet = workbook.active
    assert sheet is not None
    sheet.append(['Код', 'Название', 'Остаток', 'РРЦ', 'Ёмкость'])
    sheet.append([None, 'Раздел', None, 'РРЦ', 'А·ч'])
    sheet.append(['001', ' XTREME   +EFB 60 ', '>30', 5500.25, 60])
    workbook.save(path)
    workbook.close()
    config = _config(
        {
            'start_row': 2,
            'columns': {
                '0': 'code',
                '1': 'title',
                '2': 'rest_count',
                '3': 'price_recommended',
                '4': 'capacity_ah',
            },
        }
    )
    section = _section(config)
    battery_handler = make_battery_handler(section, 'plant')
    routing = VendorRouting(config)
    file_reader = FileReader(price_source=MagicMock())
    routing.resolve(section.id, file_reader, [str(path)])
    parsed = battery_handler.process_fields(routing.read_rows(section.id))
    assert len(parsed.positions) == 1
    position = parsed.positions[0]
    assert position.identity.code == '001'
    assert position.identity.model == 'XTREME +EFB'
    assert position.electrical.capacity_ah == 60
    assert position.offer.rest_count == 30
    assert str(position.offer.sale_price) == '5500.25'
