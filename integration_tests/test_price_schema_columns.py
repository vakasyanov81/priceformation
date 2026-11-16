"""Координаты предупреждений при обновлении реального прайса План-Т."""

import json
from pathlib import Path

from xlsxwriter import Workbook

from infrastructure.config.fake_config_provider import FakeConfigProvider
from services.price_schema_service import PriceSchemaService

_FIXTURES = Path(__file__).parent / 'parse_config_example' / 'vendors'
_EXPECTED = (
    'Поставщик «План-Т» (plant/price.xlsx), группа «аккумуляторы» (batteries): '
    'изменилась схема прайса — вкладка «TDSheet», колонка Y: '
    'заголовок «РРЦ» → «Розничная» (используется как «price_recommended»)'
)


def _plant_price(path: Path, recommended_header: str) -> None:
    """Пустая колонка A не меняет координаты X и Y."""
    with Workbook(path) as book:
        sheet = book.add_worksheet('TDSheet')
        sheet.write('B1', 'План-Т')
        sheet.write('B5', 'Наименование')
        sheet.write('X5', 'Оптовая')
        sheet.write('Y5', recommended_header)
        sheet.write('B6', 'АКБ XTREME 60')


def test_plant_header_change_column(tmp_path: Path) -> None:
    """Смена РРЦ в Y не приписывается оптовой цене из X при пустой колонке A."""
    provider = FakeConfigProvider(tmp_path)
    vendors = Path(provider.config_file('vendors'))
    vendors.mkdir()
    config = json.loads((_FIXTURES / 'plant.json').read_text(encoding='utf-8'))
    config['product_groups'][0]['file_templates'] = ['price.xlsx']
    (vendors / 'plant.json').write_text(json.dumps(config), encoding='utf-8')
    price = Path(provider.price_folder('plant')) / 'price.xlsx'
    price.parent.mkdir()
    _plant_price(price, 'РРЦ')
    service = PriceSchemaService(tmp_path / 'backup', provider)
    assert service.snapshot()

    _plant_price(price, 'Розничная')

    assert service.check() == [_EXPECTED]
