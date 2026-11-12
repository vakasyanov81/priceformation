"""Карты Запаски сохраняют цены, остатки и характеристики исходного JSON."""

import pytest

from infrastructure.config.fake_config_provider import FakeConfigProvider
from parsers.base_parser.routing_rows import map_row
from parsers.base_parser.section_params import parser_params_from_section
from parsers.raw_table import RawRow
from parsers.vendor_config.provider import load_vendor_configs


@pytest.mark.parametrize('section_id', ['2', '22'])
def test_zapaska_json_preserves_offer_and_dimensions(
    example_vendors_provider: FakeConfigProvider,
    section_id: str,
) -> None:
    config = load_vendor_configs(example_vendors_provider)['zapaska']
    section = next(section for section in config.sections if section.id == section_id)
    source = {
        'cae': '001',
        'name': 'Название поставщика',
        'price': 5000,
        'rest': 4,
        'width': '205',
        'diameter': '16',
        'model': 'Модель',
        'season': 'Зимняя',
        'color': 'Silver',
        'ext_diameter': 31,
    }

    mapped = map_row(config, RawRow(source, 1), parser_params_from_section(section, config.folder))

    assert mapped['code_art'] == '001'
    assert mapped['title'] == source['name']
    assert mapped['price_opt'] == source['price']
    assert mapped['rest_count'] == source['rest']
    assert mapped['width'] == source['width']
    assert mapped['diameter'] == source['diameter']
    assert mapped['model'] == source['model']
    assert mapped['season'] == source['season']
    assert mapped['color'] == source['color']
    assert mapped['ext_diameter'] == source['ext_diameter']
