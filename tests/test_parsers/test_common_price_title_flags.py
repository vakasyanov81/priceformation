"""Признаки из названия для ключа: XL, вентиль, модель камеры и ободной ленты."""

import pytest

from domain.row_item.row_item import RowItem
from parsers.common_price.title_flags import tube_model, valve_key


def _row(title: str, kind: str) -> RowItem:
    return RowItem({'title': title, 'type_production': kind})


@pytest.mark.parametrize(
    ('title', 'expected'),
    [
        ('Камера СВК 11.00-20 ГК-145 (0)', 'ГК-145'),
        ('Камера 6.45-13 УК-13М ОШЗ', 'УК-13М'),
        ('Камера СВК УК-13 М (6.45-13) ЛК (25)', 'УК-13М'),
        ('Камера 215 R16 Гк-115 ОШЗ', 'ГК-115'),
        ('Камера СВК 14.00-20 РК-5А-145 (0)', 'РК-5А-145'),
        ('Камера УК-14-02 ВолШЗ', 'УК-14-02'),
        ('Автокамера 11.2-20', ''),
        ('Камера 12.5/80-18 Китай', ''),
        ('Камера СВК 11.2-20 ТК (48), (1 шт)', ''),
    ],
)
def test_camera_model(title: str, expected: str) -> None:
    assert tube_model(_row(title, 'Автокамера')) == expected


@pytest.mark.parametrize(
    ('title', 'expected'),
    [('Ободная лента 300-508А', '300-508А'), ('300-508 (14.00-20) об/лента', ''), ('Ободная лента 23.5-25', '')],
)
def test_rim_tape_model(title: str, expected: str) -> None:
    assert tube_model(_row(title, 'Ободная лента')) == expected


def test_tube_model_is_empty_for_tire() -> None:
    assert tube_model(_row('16.5/70-18 КФ-97 149A6 10PR TT', 'Легковая шина')) == ''


def test_valve_is_empty_for_disk() -> None:
    disk = _row('16 Trebl 5.5*16 с вентилем', 'Диск')
    assert valve_key(disk) == ''
