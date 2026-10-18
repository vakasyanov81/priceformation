"""Разбор названия камер и ободных лент: размер."""

import pytest

from domain.row_item.row_item import RowItem
from parsers.strategies._tire_title_parser import parse_tire_title
from parsers.strategies._tube_title_parser import TubeTitleParts, fill_tube_fields, parse_tube_title


@pytest.mark.parametrize(
    ('raw', 'width', 'height', 'diameter', 'ext'),
    [
        ('Камера СВК 20.5-25 ГК-260 (0)', '20.5', '', '25', ''),
        ('Автокамера 5.00-8', '5.00', '', '8', ''),
        ('Автокамера 12.5/80-18', '12.5', '80', '18', ''),
        ('Камера СВК 10.0/75-15.3 ЛК (50)', '10.0', '75', '15.3', ''),
        ('Камера СВК 600/55-26.5 ТК (135)', '600', '55', '26.5', ''),
        ('Камера СВК 1200х500-508 РК-5А-145 (65)', '500', '', '508', '1200'),
        ('Камера СВК 1220-400-533 SUNTOP+монтажный комплект', '400', '', '533', '1220'),
        ('Камера 1200-500-508 ОШЗ', '500', '', '508', '1200'),
        ('Камера СВК 15.5-18/16.5-18 ГК-115 (60)', '15.5', '', '18', ''),
        ('Камера СВК 710/70-38 (620/70-42) ТК (156)', '710', '70', '38', ''),
        ('Камера СВК 30.5L-32 ТК (200)', '30.5', '', '32', ''),
        ('Камера 175-13 TR13 FUCHUN', '175', '', '13', ''),
        ('Камера 215 R16 Гк-115 ОШЗ', '215', '', '16', ''),
        ('камера Triangle 11.2-20', '11.2', '', '20', ''),
        ('Ободная лента 16/70-20 (300-508)', '16', '70', '20', ''),
        ('Ободная лента 300-508А', '300', '', '508', ''),
        ('Ободная лента 340-533 (1220*400-533) Nortec', '340', '', '533', ''),
        ('камера 175/185-16 Ecotech', '175', '', '16', ''),
        ('130-10 об/лента', '130', '', '10', ''),
        ('16.00-24 об/лента', '16.00', '', '24', ''),
        ('205-457 (12.00-18) об/лента', '205', '', '457', ''),
    ],
)
def test_parse_size(raw: str, width: str, height: str, diameter: str, ext: str) -> None:
    """Размер из каждого формата названия камеры/ленты."""
    parts = parse_tube_title(raw)

    assert parts is not None
    assert (parts.width, parts.height_percent) == (width, height)
    assert (parts.diameter, parts.ext_diameter) == (diameter, ext)


@pytest.mark.parametrize(
    'raw',
    ['Камера УК-14-02 ВолШЗ', 'Камера УК-14М ОШЗ', '215/75R17.5 Triangle TR685', 'Диск штамп 5x10', 'лента', '', None],
)
def test_foreign_or_unreadable_title(raw: str | None) -> None:
    """Не камера или размер не читается — None."""
    assert parse_tube_title(raw) is None


def test_tire_parser_ignores_tube() -> None:
    """Камера с `R` в размере — не шина: модель вроде «Камера Гк-115» не появляется."""
    assert parse_tire_title('Камера 215 R16 Гк-115 ОШЗ') is None


def test_fill_keeps_existing_values() -> None:
    row = RowItem({'title': 'Камера 175-13 ОШЗ'})
    row.set_field('diameter', '14')
    parts = parse_tube_title('Камера 175-13 ОШЗ')
    assert parts is not None

    fill_tube_fields(row, parts)

    assert (row.tire.width, row.tire.diameter) == ('175', '14')


@pytest.mark.parametrize('raw', ['130-10 об/лента', '205-457 (12.00-18) об/лента'])
def test_tire_parser_ignores_tape_without_prefix(raw: str) -> None:
    """Лента без префикса — не шина: `об/лента` не становится брендом, конструкция не заполняется."""
    assert parse_tire_title(raw) is None


def test_profile_at_upper_bound_is_kept() -> None:
    """Профиль ровно 100 % — ещё профиль, а не вторая ширина."""
    parts = parse_tube_title('Автокамера 12.5/100-18')
    assert parts is not None
    assert parts.height_percent == '100'


def test_fill_writes_all_size_fields() -> None:
    """Все четыре параметра размера попадают в поля позиции под своими именами."""
    row = RowItem({})
    fill_tube_fields(row, TubeTitleParts(width='12.5', height_percent='80', diameter='18', ext_diameter='1200'))
    tire = row.tire
    assert (tire.width, tire.height_percent) == ('12.5', '80')
    assert (tire.diameter, tire.ext_diameter) == ('18', 1200)
