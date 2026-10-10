"""Разбор и сборка названия номенклатуры STK."""

import pytest

from domain.row_item.row_item import RowItem
from parsers.strategies._stk_title_helper import (
    fill_stk_fields,
    parse_stk_title,
)

# Примеры склейки STK → Пионер (порядок: размер бренд модель нагрузка/скорость PR камера назначение).
_GLUE_EXAMPLES = (
    (
        'Автошина 11R22.5 16PR 146/143L GREENSTONE DR668 шашка',
        '11R22.5 GREENSTONE DR668 146/143L 16PR шашка',
    ),
    (
        'Автошина 235/75R17,5 LingLong LLA78 18PR 143/141J TL трал',
        '235/75R17.5 LingLong LLA78 143/141J 18PR TL трал',
    ),
    (
        'Автошина 12.00R24 DRC D931 20PR 160/157F TTF карьер',
        '12.00R24 DRC D931 160/157F 20PR TTF карьер',
    ),
    (
        'Автошина 7.00 R16LT14PR 118/114L GREENSTONE ST896 змейка',
        '7.00R16LT GREENSTONE ST896 118/114L 14PR змейка',
    ),
    (
        'Автошина 295/80R22.5 18PR 152/149M GREENSTONE ST33 руль',
        '295/80R22.5 GREENSTONE ST33 152/149M 18PR руль',
    ),
    (
        'Автошина 385/55R22.5 20PR 160K GREENSTONE ST398 руль/прицеп',
        '385/55R22.5 GREENSTONE ST398 160K 20PR руль/прицеп',
    ),
    (
        'Автошина 315/80 R22.5 22PR 167/164D TRANSMATE TMD18 карьер',
        '315/80R22.5 TRANSMATE TMD18 167/164D 22PR карьер',
    ),
)


@pytest.mark.parametrize(('raw', 'expected'), _GLUE_EXAMPLES)
def test_parse_and_compose_examples(raw: str, expected: str) -> None:
    """Склейка примера даёт порядок Пионера."""
    parts = parse_stk_title(raw)

    assert parts is not None
    assert parts.compose() == expected


@pytest.mark.parametrize(('raw', 'expected'), _GLUE_EXAMPLES)
def test_compose_uses_brand_over_parsed(raw: str, expected: str) -> None:
    """Канонический бренд из поля перекрывает разобранный токен."""
    parts = parse_stk_title(raw)

    assert parts is not None
    assert parts.compose('Brand') == expected.replace(parts.brand, 'Brand', 1)


def test_parse_splits_size_and_parameters() -> None:
    """Размер и параметры разобраны по отдельным полям."""
    parts = parse_stk_title('Автошина 235/75R17,5 LingLong LLA78 18PR 143/141J TL трал')

    assert parts is not None
    assert parts.size.label == '235/75R17.5'
    assert parts.size.width == '235'
    assert parts.size.height_percent == '75'
    assert parts.size.diameter == '17.5'
    assert (parts.brand, parts.model) == ('LingLong', 'LLA78')
    assert (parts.load, parts.velocity) == ('143/141', 'J')
    assert (parts.layering, parts.intimacy) == ('18PR', 'TL')
    assert parts.usage == ('трал',)


def test_parse_joins_split_size_and_pr() -> None:
    """Пробел внутри размера убран, ``PR`` отделён от ``LT``."""
    parts = parse_stk_title('Автошина 7.00 R16LT14PR 118/114L GREENSTONE ST896 змейка')

    assert parts is not None
    assert parts.size.label == '7.00R16LT'
    assert parts.size.width == '7.00'
    assert parts.size.height_percent == ''
    assert parts.size.diameter == '16'
    assert parts.layering == '14PR'
    assert parts.load == '118/114'
    assert parts.velocity == 'L'


def test_parse_without_kind_prefix() -> None:
    """Размер в начале названия разбирается и без слова «Автошина»."""
    parts = parse_stk_title('11R22.5 GREENSTONE DR668 146/143L 16PR шашка')

    assert parts is not None
    assert parts.brand == 'GREENSTONE'
    assert parts.model == 'DR668'
    assert parts.usage == ('шашка',)


def test_parse_returns_none_for_disk() -> None:
    """Диск — не размер шины: разбор не срабатывает."""
    assert parse_stk_title('Диск стальной YONGZHENG 22,5*11,75 10 26мм ЕТ0 D281') is None


def test_parse_returns_none_without_brand_model() -> None:
    """Только размер и служебные токены — модели нет, разбор пуст."""
    assert parse_stk_title('Автошина 11R22.5 16PR 146/143L') is None


def test_fill_stk_fields_sets_parameters() -> None:
    """Разобранные параметры попадают в поля позиции."""
    row = RowItem({'title': 'Автошина 11R22.5 16PR 146/143L GREENSTONE DR668 шашка'})
    parts = parse_stk_title(row.identity.title or '')

    assert parts is not None
    fill_stk_fields(row, parts)

    assert row.tire.width == '11'
    assert row.tire.height_percent is None
    assert row.tire.diameter == '22.5'
    assert row.tire.layering == '16PR'
    assert row.tire.index_load == '146/143'
    assert row.tire.index_velocity == 'L'
    assert row.identity.model == 'DR668'


def test_fill_stk_fields_keeps_existing_values() -> None:
    """Уже заполненные поля разбор не перетирает."""
    row = RowItem(
        {
            'title': 'Автошина 11R22.5 16PR 146/143L GREENSTONE DR668 шашка',
            'width': '999',
            'model': 'Old',
        },
    )
    parts = parse_stk_title(row.identity.title or '')

    assert parts is not None
    fill_stk_fields(row, parts)

    assert row.tire.width == '999'
    assert row.identity.model == 'Old'
