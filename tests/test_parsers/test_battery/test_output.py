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
from parsers.battery.output import BatteryOutputSource
from parsers.battery.output_fields import OUTPUT_FIELDS
from parsers.vendor_config.group_models import BatteryConfig
from parsers.vendor_config.models import VendorConfig
from parsers.writer.output_plan import prepare_output_plan
from parsers.writer.templates.group_output import GroupOutput
from parsers.writer.templates.group_templates import group_template_output
from parsers.writer.templates.tmpl.for_batteries import ForBatteries
from parsers.writer.templates.tmpl.for_drom import ForDrom
from tests.group_output_examples import group_writer


def _source() -> BatteryOutputSource:
    position = BatteryItem.from_fields(
        {
            'title': 'XTREME Arctic 60',
            'code': '001',
            'price_opt': '4000.10',
            'price_recommended': '5500.20',
            'rest_count': 1,
            'efb': False,
            'length_mm': '302.0',
            'width_mm': '172.0',
            'height_mm': '220.0',
            'weight': '24.0',
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


@pytest.mark.parametrize(
    'price, expected',
    [
        ('14500.0', '14500'),
        ('14500.00', '14500'),
        ('14500.25', '14500.25'),
    ],
)
def test_battery_whole_prices_have_no_fraction(price: str, expected: str) -> None:
    """Цены АКБ теряют нулевую дробную часть на границе записи."""
    position = BatteryItem.from_fields({'price_opt': price, 'price_recommended': price})
    source = BatteryOutputSource(BatteryResult((position,)))
    group = ForBatteries().output_spec().groups[0]
    row = source.prepare('for_batteries', group)[0]

    assert row['price_opt'] == row['price_recommended'] == row['sale_price'] == expected
    assert str(position.offer.price_opt) == price


def test_output_filters_do_not_change_package() -> None:
    source = _source()
    group = ForBatteries().output_spec().groups[0]
    filtered = replace(group, filters={'is_main': [False]})
    assert source.prepare('for_batteries', filtered) == ()
    assert len(source.prepare('for_batteries', group)) == 1
    assert BatteryOutputSource(BatteryResult()).prepare('for_batteries', group) == ()


@pytest.mark.parametrize('field', ['length_mm', 'width_mm', 'height_mm', 'weight', 'capacity_ah', 'starting_current_a'])
@pytest.mark.parametrize(
    'number, expected',
    [
        ('24.0', '24'),
        ('24.00', '24'),
        ('13.9', '13.9'),
    ],
)
def test_battery_measurements_omit_zero_fraction(field: str, number: str, expected: str) -> None:
    """Числовые характеристики выводятся без нулевой дробной части, точность сохраняется."""
    position = BatteryItem.from_fields({field: number})
    source = BatteryOutputSource(BatteryResult((position,)))
    group = ForBatteries().output_spec().groups[0]

    assert source.prepare('for_batteries', group)[0][field] == expected


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


def test_output_rejects_settings_of_another_group_with_exact_message() -> None:
    group = replace(ForBatteries().output_spec().groups[0], id=ProductGroup.TIRE_AND_DISK)

    with pytest.raises(ValueError) as caught:
        _source().prepare('for_batteries', group)

    assert str(caught.value) == 'Преобразователь batteries получил настройки другой группы'


def test_output_rejects_merged_warehouses_with_exact_message() -> None:
    group = replace(ForBatteries().output_spec().groups[0], merge_warehouses=True)

    with pytest.raises(ValueError) as caught:
        _source().prepare('for_batteries', group)

    assert str(caught.value) == 'batteries: сведение складов недоступно без отдельных складских данных'


def test_battery_template_writes_prices_and_stock(tmp_path: Path) -> None:
    template = ForBatteries().output_spec()
    sources = {ProductGroup.BATTERIES: _source()}
    plan = prepare_output_plan([template], sources, current_date='2026-11-12')
    assert plan[0].sheets[0].title_fields == frozenset(('title',))
    paths = group_writer(tmp_path).write([template], sources, current_date='2026-11-12')
    workbook = load_workbook(paths[0])
    sheet = workbook['Аккумуляторы']
    header, cells = list(sheet.values)
    assert list(header) == [
        'Название',
        'Производитель',
        'Полярность',
        'Емкость',
        'Пусковой ток',
        'Длина',
        'Ширина',
        'Высота',
        'Типоразмер',
        'Остаток',
        'Закупочная цена',
        'РРЦ',
        'Цена продажи',
        'Наценка в руб',
        'Наценка в %',
        'Клеммы',
        'EFB',
        'AGM',
        'Крепление',
        'Обслуживаемость',
        'Вес',
        'Гарантия',
        'Поставщик',
        'Ценовая группа',
    ]
    row = dict(zip(header, cells, strict=True))
    assert row['Наценка в руб'] == '1500.10'
    assert row['Наценка в %'] == '37.50'
    assert row['Цена продажи'] == row['РРЦ'] == '5500.20'
    assert row['Закупочная цена'] == '4000.10'
    assert row['Остаток'] == 1
    assert row['Длина'] == '302'
    assert row['Ширина'] == '172'
    assert row['Высота'] == '220'
    assert row['Вес'] == '24'
    assert row['EFB'] is None
    workbook.close()


def test_drom_battery_defaults_format_and_empty_stock_filter(tmp_path: Path) -> None:
    """Дром получает доступные АКБ с фиксированными наличием, состоянием и текстовой ценой."""
    available = BatteryItem.from_fields({'title': 'Доступен', 'rest_count': 1, 'price_markup': '5000'})
    without_stock = BatteryItem.from_fields({'title': 'Нет остатка', 'rest_count': None})
    source = BatteryOutputSource(BatteryResult((available, without_stock)))
    template = group_template_output(ForDrom)
    paths = group_writer(tmp_path).write(
        [replace(template, groups=(template.groups[1],))],
        {ProductGroup.BATTERIES: source},
        selected={ProductGroup.BATTERIES},
    )
    workbook = load_workbook(paths[0])
    sheet = workbook['Аккумуляторы']
    header, cells = list(sheet.values)
    row = dict(zip(header, cells, strict=True))
    assert row['Номенклатура'] == 'Доступен'
    assert row['Цена'] == '5000'
    assert sheet['D2'].number_format == '@'
    assert row['Наличие'] == 'В наличии'
    assert row['Состояние'] == 'Новое'
    workbook.close()


@pytest.mark.parametrize(
    'field, title, characteristic',
    [
        ('capacity_ah', 'Ёмкость, А·ч', '60'),
        ('starting_current_a', 'Пусковой ток, А', '600'),
        ('length_mm', 'Длина, мм', '302'),
        ('width_mm', 'Ширина, мм', '172'),
        ('height_mm', 'Высота, мм', '220'),
        ('terminal_type', 'Тип клемм', 'стандарт'),
        ('size_type', 'Типоразмер', 'JIS D31'),
        ('polarity', 'Полярность', 'обратная (0, L)'),
        ('serviceable', 'Обслуживаемость', True),
        ('weight', 'Вес', '13.9'),
        ('bottom_mount', 'Нижнее крепление', 'B01'),
        ('efb', 'EFB', True),
        ('agm', 'AGM', True),
    ],
)
def test_drom_battery_characteristics_reach_workbook(
    tmp_path: Path, field: str, title: str, characteristic: str | bool
) -> None:
    """Прайс Дром сохраняет дополнительные характеристики аккумулятора."""
    position = BatteryItem.from_fields({field: characteristic, 'rest_count': 1})
    source = BatteryOutputSource(BatteryResult((position,)))
    template = group_template_output(ForDrom)
    paths = group_writer(tmp_path).write(
        [replace(template, groups=(template.groups[1],))],
        {ProductGroup.BATTERIES: source},
        selected={ProductGroup.BATTERIES},
    )
    workbook = load_workbook(paths[0])
    header, cells = list(workbook['Аккумуляторы'].values)
    row = dict(zip(header, cells, strict=True))
    expected = 'Да' if characteristic is True else characteristic
    assert row[title] == expected
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


@pytest.mark.parametrize(
    'purchase, recommended, sale, absolute, percent',
    [
        ('100', '150', '120', '20', '20'),
        ('100', '150', None, '50', '50'),
        ('300', None, '400', '100', '33.33'),
        ('100', None, '100', '0', '0'),
        ('100', None, '90', '-10', '-10'),
        ('0', None, '100', '100', None),
        (None, None, '100', None, None),
        ('100', None, None, None, None),
    ],
)
def test_output_markup_uses_final_sale(
    purchase: str | None,
    recommended: str | None,
    sale: str | None,
    absolute: str | None,
    percent: str | None,
) -> None:
    """Наценка считается от итоговой цены с сохранением неизвестных значений."""
    position = BatteryItem.from_fields({'price_opt': purchase, 'price_recommended': recommended, 'price_markup': sale})
    source = BatteryOutputSource(BatteryResult((position,)))
    group = ForBatteries().output_spec().groups[0]
    row = source.prepare('for_batteries', group)[0]
    assert row['absolute_markup'] == absolute
    assert row['percent_markup'] == percent
