"""Golden-тесты формы строки: to_dict(), колонки шаблонов, xlsx и jsonl.

Эталон зафиксирован до разбиения RowItem на value objects (#246) и защищает
сериализационный контракт: набор ключей, их порядок и приведённые значения.
"""

import json
from pathlib import Path
from typing import Any

import pytest

from domain.row_item.row_item import RowItem
from parsers.writer.fake_driver import FakeXlwtDriver
from parsers.writer.jsonl_writer import write_template_jsonl
from parsers.writer.templates.column_helper import ColumnHelper
from parsers.writer.templates.iwrite_template import IWriteTemplate
from parsers.writer.templates.tmpl.for_doubles import ForDoubles
from parsers.writer.templates.tmpl.for_drom import ForDrom
from parsers.writer.templates.tmpl.for_full import ForFull
from parsers.writer.templates.tmpl.for_inner import ForInner
from parsers.writer.xls_writer import XlsWriter, get_value

type CellValue = tuple[str, Any]
type ColumnCells = list[CellValue]

RAW_ROW: dict[str, Any] = {
    'code': 87674341266.0,
    'code_man': '  77-15 ',
    'code_art': '1101.5',
    'title': '  225/40R18 Crossleader 92Y  ',
    'manufacturer_name': ' crossleader ',
    'brand': 'CROSSLEADER',
    'model': 'DSU02',
    'price_opt': '3 457,50',
    'price_recommended': '',
    'price_markup': 3980,
    'percent_markup': '15,13',
    'supplier_name': 'Мим',
    'type_production': 'Автошина',
    'rest_count': 4.0,
    'reserve_count': '2',
    'delivery_period': 3,
    'condition': 'Новое',
    'available': 'В наличии',
    'season': 'Зима',
    'spike': 'Шипы',
    'width': '225',
    'height_percent': '40',
    'mark': 'CROSSLEADER',
    'diameter': '18',
    'ext_diameter': 18.0,
    'disk_thickness': '7',
    'slot_count': '5',
    'us_aff_designation': 'Y',
    'pcd1': '114.3',
    'pcd2': 100,
    'eet': '40',
    'central_diameter': '60.1',
    'color': 'чёрный',
    'main_color': 'серебристый',
    'tire_type': 'R',
    'inscription_on_the_side': 'XL',
    'run_flat': 'да',
    'index_velocity': 'Y',
    'index_load': '92',
    'construction_type': 'радиальная',
    'axis': 'ведущая',
    'layering': '2',
    'intimacy': 'камерная',
    'camera_type': 'камера',
    'fastener': '5x114,3',
    'disk_type': 'литой',
    'disk_type_1': 'легковой',
    'order': 3,
    'group_by_params': 77,
    'double_candidate': True,
    'is_double': False,
    'disputed': 'по размеру',
    'profile': '40',
    'hash_title': 'deadbeef',
    'codes': '1,2',
}

GOLDEN_TO_DICT: list[CellValue] = [
    ('code', '87674341266'),
    ('code_man', '77-15'),
    ('code_art', '1101.5'),
    ('title', '225/40R18 Crossleader 92Y'),
    ('manufacturer_name', 'crossleader'),
    ('brand', 'CROSSLEADER'),
    ('model', 'DSU02'),
    ('price_opt', 3457.5),
    ('price_recommended', 0.0),
    ('price_markup', 3980.0),
    ('percent_markup', 15.13),
    ('supplier_name', 'Мим'),
    ('type_production', 'Автошина'),
    ('rest_count', 4),
    ('reserve_count', 2),
    ('delivery_period', 3),
    ('condition', 'Новое'),
    ('available', 'В наличии'),
    ('season', 'Зима'),
    ('spike', 'Шипы'),
    ('width', '225'),
    ('height_percent', '40'),
    ('mark', 'CROSSLEADER'),
    ('diameter', '18'),
    ('ext_diameter', 18),
    ('disk_thickness', '7'),
    ('slot_count', 5),
    ('us_aff_designation', 'Y'),
    ('pcd1', 114.3),
    ('pcd2', '100'),
    ('eet', 40),
    ('central_diameter', 60.1),
    ('color', 'чёрный'),
    ('main_color', 'серебристый'),
    ('tire_type', 'R'),
    ('inscription_on_the_side', 'XL'),
    ('run_flat', 'да'),
    ('index_velocity', 'Y'),
    ('index_load', '92'),
    ('construction_type', 'радиальная'),
    ('axis', 'ведущая'),
    ('layering', '2'),
    ('intimacy', 'камерная'),
    ('camera_type', 'камера'),
    ('fastener', '5x114,3'),
    ('disk_type', 'литой'),
    ('disk_type_1', 'легковой'),
    ('order', '3'),
    ('group_by_params', 77),
    ('double_candidate', True),
    ('is_double', False),
    ('disputed', 'по размеру'),
    ('profile', '40'),
    ('hash_title', 'deadbeef'),
    ('codes', '1,2'),
]

GOLDEN_TEMPLATE_VALUES: dict[str, ColumnCells] = {
    'ForDrom': [
        ('Тип товара', 'Автошина'),
        ('Бренд', 'crossleader'),
        ('Номенклатура', '225/40R18 Crossleader 92Y'),
        ('Сезон', 'Зима'),
        ('Шип', 'Шипы'),
        ('Цена', 3980.0),
        ('Остаток', 4),
        ('Наличие', 'В наличии'),
        ('Срок доставки', 3),
        ('Состояние', 'Новое'),
    ],
    'ForInner': [
        ('Тип товара', 'Автошина'),
        ('Бренд', 'crossleader'),
        ('Номенклатура', '225/40R18 Crossleader 92Y'),
        ('Сезон', 'Зима'),
        ('Шип', 'Шипы'),
        ('Цена закуп.', 3457.5),
        ('Цена', 3980.0),
        ('Рекомендуемая Цена', None),
        ('Наценка %', 15.13),
        ('Остаток', 4),
        ('Поставщик', 'Мим'),
        ('Наличие', 'В наличии'),
        ('Срок доставки', 3),
        ('Состояние', 'Новое'),
    ],
    'ForFull': [
        ('Тип товара', 'Автошина'),
        ('Бренд', 'crossleader'),
        ('Brand', 'CROSSLEADER'),
        ('Марка', 'CROSSLEADER'),
        ('Модель', 'DSU02'),
        ('Номенклатура', '225/40R18 Crossleader 92Y'),
        ('Код', '87674341266'),
        ('Код производителя', '77-15'),
        ('Артикул', '1101.5'),
        ('Поставщик', 'Мим'),
        ('Сезон', 'Зима'),
        ('Шип', 'Шипы'),
        ('Ширина', '225'),
        ('Профиль', '40'),
        ('Диаметр', '18'),
        ('Внешний диаметр', 18),
        ('Индекс нагрузки', '92'),
        ('Индекс скорости', 'Y'),
        ('Тип шины', 'R'),
        ('RunFlat', 'да'),
        ('Надпись на боковине', 'XL'),
        ('Тип конструкции', 'радиальная'),
        ('Ось', 'ведущая'),
        ('Слойность', '2'),
        ('Камерность', 'камерная'),
        ('Тип камеры', 'камера'),
        ('US обозначение', 'Y'),
        ('Толщина диска', '7'),
        ('Кол-во отверстий', 5),
        ('PCD', 114.3),
        ('PCD2', '100'),
        ('ET', 40),
        ('DIA', 60.1),
        ('Крепеж', '5x114,3'),
        ('Тип диска', 'литой'),
        ('Вид диска', 'легковой'),
        ('Цвет', 'чёрный'),
        ('Основной цвет', 'серебристый'),
        ('Цена закуп.', 3457.5),
        ('Цена', 3980.0),
        ('Рекомендуемая Цена', None),
        ('Наценка %', 15.13),
        ('Остаток', 4),
        ('Резерв', 2),
        ('Наличие', 'В наличии'),
        ('Срок доставки', 3),
        ('Состояние', 'Новое'),
    ],
    'ForDoubles': [
        ('Тип товара', 'Автошина'),
        ('Бренд', 'crossleader'),
        ('Номенклатура', '225/40R18 Crossleader 92Y'),
        ('Сезон', 'Зима'),
        ('Шип', 'Шипы'),
        ('Цена закуп.', 3457.5),
        ('Цена', 3980.0),
        ('Рекомендуемая Цена', None),
        ('Наценка %', 15.13),
        ('Остаток', 4),
        ('Поставщик', 'Мим'),
        ('Наличие', 'В наличии'),
        ('Срок доставки', 3),
        ('Состояние', 'Новое'),
        ('Группа по параметрам', 77),
        ('Дубль', None),
        ('Главный дубль', True),
        ('Спорная', 'по размеру'),
    ],
}

GOLDEN_DROM_BODY: dict[str, Any] = {
    'cell(1,0)': 'Автошина',
    'cell(1,1)': 'crossleader',
    'cell(1,2)': '225/40R18 Crossleader 92Y',
    'cell(1,3)': 'Зима',
    'cell(1,4)': 'Шипы',
    'cell(1,5)': 3980.0,
    'cell(1,6)': 4,
    'cell(1,7)': 'В наличии',
    'cell(1,8)': 3,
    'cell(1,9)': 'Новое',
}

GOLDEN_DROM_HEAD: list[str] = [
    'Тип товара',
    'Бренд',
    'Номенклатура',
    'Сезон',
    'Шип',
    'Цена',
    'Остаток',
    'Наличие',
    'Срок доставки',
    'Состояние',
]

GOLDEN_DROM_JSONL = (
    '{"1":"Автошина","2":"crossleader","3":"225/40R18 Crossleader 92Y","4":"Зима","5":"Шипы",'
    '"6":3980.0,"7":4,"8":"В наличии","9":3,"10":"Новое"}\n'
)

_ALL_TEMPLATES = (ForInner, ForDrom, ForFull, ForDoubles)


def test_to_dict_keeps_keys_order_and_values() -> None:
    """to_dict отдаёт ровно те же ключи, в том же порядке, с теми же значениями."""
    assert list(RowItem(RAW_ROW).to_dict().items()) == GOLDEN_TO_DICT


def test_golden_row_has_no_parse_errors() -> None:
    """эталонная строка разбирается без ошибок приведения."""
    assert RowItem(RAW_ROW).parse_errors == {}


def test_broken_value_leaves_field_unset() -> None:
    """неприводимое поле не попадает в to_dict, ошибка попадает в parse_errors."""
    row = RowItem({'title': 't1', 'price_opt': 'не число'})
    assert 'price_opt' not in row.to_dict()
    assert row.parse_errors == {
        'price_opt': {'value': 'не число', 'error': "could not convert string to float: 'нечисло'"}
    }


def _template_cells(template: type[IWriteTemplate], row: dict[str, Any]) -> ColumnCells:
    """Значение каждой колонки шаблона, прочитанное из плоской строки."""
    cells: ColumnCells = []
    for column in template().columns():
        helper = ColumnHelper(column)
        cells.append((helper.name, get_value(column, row)))
    return cells


@pytest.mark.parametrize('template', _ALL_TEMPLATES, ids=lambda template: template.__name__)
def test_template_columns_match_golden(template: type[IWriteTemplate]) -> None:
    """каждая колонка каждого шаблона читает то же значение из плоской строки."""
    assert _template_cells(template, RowItem(RAW_ROW).to_dict()) == GOLDEN_TEMPLATE_VALUES[template.__name__]


def test_drom_xlsx_head_and_body_match_golden(tmp_path: Path) -> None:
    """шапка и тело листа drom совпадают с эталоном."""
    driver = FakeXlwtDriver()
    row = RowItem(RAW_ROW).to_dict()
    XlsWriter(driver, [row], ForDrom, result_folder=str(tmp_path)).write()
    assert driver.head == GOLDEN_DROM_HEAD
    assert driver.body == GOLDEN_DROM_BODY


def test_drom_jsonl_matches_golden(tmp_path: Path) -> None:
    """jsonl drom совпадает с эталоном байт в байт."""
    path = write_template_jsonl([RowItem(RAW_ROW).to_dict()], ForDrom, str(tmp_path))
    assert Path(path).read_text(encoding='utf-8') == GOLDEN_DROM_JSONL


def test_drom_meta_matches_golden(tmp_path: Path) -> None:
    """result_meta.json drom: колонки в порядке шаблона, кодовника повторов нет."""
    write_template_jsonl([RowItem(RAW_ROW).to_dict()], ForDrom, str(tmp_path))
    meta_path = tmp_path / 'result_meta.json'
    loaded = json.loads(meta_path.read_text(encoding='utf-8'))
    numbers = map(str, range(1, len(GOLDEN_DROM_HEAD) + 1))
    assert loaded == dict(zip(numbers, GOLDEN_DROM_HEAD, strict=True))
