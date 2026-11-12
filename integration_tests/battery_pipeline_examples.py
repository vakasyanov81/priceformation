"""Эталон План-Т и дополнительный шинный прайс того же поставщика."""

import json
import shutil
from pathlib import Path

from openpyxl import Workbook

from infrastructure.config.fake_config_provider import FakeConfigProvider

FIXTURES = Path(__file__).parent
BATTERIES = 'batteries'
TIRES = 'tire_and_disk'


def supplier_environment(root: Path) -> FakeConfigProvider:
    """Изолировать две реальные модели и общий маршрут поставщика от рабочих файлов."""
    provider = FakeConfigProvider(root)
    vendor_file = Path(provider.config_file('vendors/plant.json'))
    vendor_file.parent.mkdir()
    raw = json.loads((FIXTURES / 'parse_config_example/vendors/plant.json').read_text())
    raw['product_groups'][0]['file_templates'] = ['ПРАЙС 200 PLAN-T.PRO*.xlsx']
    raw['product_groups'].insert(0, _tire_group())
    vendor_file.write_text(json.dumps(raw, ensure_ascii=False))
    Path(provider.config_file('black_list')).write_text('')
    Path(provider.config_file('manufacturer_aliases.json')).write_text('{}')
    prices = Path(provider.price_folder('plant'))
    prices.mkdir()
    for source in (FIXTURES / 'file_prices_for_test/plant').iterdir():
        shutil.copyfile(source, prices / source.name)
    _tire_price(prices / 'tires.xlsx')
    return provider


def _tire_group() -> dict[str, object]:
    return {
        'id': TIRES,
        'file_templates': ['tires.xlsx'],
        'start_row': 2,
        'columns': {'0': 'title', '1': 'price_opt', '2': 'rest_count'},
        'sections': [{'id': 'plant_tires', 'sheet_indexes': [0]}],
    }


def _tire_price(path: Path) -> None:
    workbook = Workbook()
    sheet = workbook.active
    assert sheet is not None
    sheet.append(['Название', 'Цена', 'Остаток'])
    sheet.append(['205/55R16', 5000, 10])
    sheet.append(['195/65R15', 3500, 5])
    workbook.save(path)
    workbook.close()


def battery_rows(paths: list[str], *, shared: bool) -> list[dict[str, object]]:
    """Проверить физические листы и прочитать аккумуляторные значения по заголовкам."""
    from openpyxl import load_workbook

    for path in paths:
        workbook = load_workbook(path)
        if 'Аккумуляторы' in workbook.sheetnames:
            if shared:
                assert workbook.sheetnames == ['Шины и диски', 'Аккумуляторы']
                assert workbook['Шины и диски'].max_row == 3
            header, *rows = workbook['Аккумуляторы'].values
            workbook.close()
            return [dict(zip(header, row, strict=True)) for row in rows]
        workbook.close()
    raise AssertionError('Не найден аккумуляторный лист')


def title_corrections(path: Path, pairs: list[tuple[str | None, str]]) -> None:
    """Записать пользовательские исправления названий для проверки границ групп."""
    workbook = Workbook()
    sheet = workbook.active
    assert sheet is not None
    sheet.title = 'Sheet1'
    sheet.append(['Исходное название', 'Исправление'])
    for pair in pairs:
        sheet.append(pair)
    workbook.save(path)
    workbook.close()
