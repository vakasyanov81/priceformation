"""Стратегия слота `title` для STK: сборка названия шины в порядке Пионера."""

import pytest

from domain.row_item.row_item import RowItem
from parsers.strategies.stk_title import StkTireCompose


@pytest.mark.parametrize(
    ('raw', 'expected'),
    [
        (
            'Автошина 11R22.5 16PR 146/143L GREENSTONE DR668 шашка',
            '11R22.5 GREENSTONE DR668 146/143L 16PR шашка',
        ),
        (
            'Автошина 235/75R17,5 LingLong LLA78 18PR 143/141J TL трал',
            '235/75R17.5 LingLong LLA78 143/141J 18PR TL трал',
        ),
        (
            'Автошина 7.00 R16LT14PR 118/114L GREENSTONE ST896 змейка',
            '7.00R16LT GREENSTONE ST896 118/114L 14PR змейка',
        ),
        (
            'Автошина 12.00R24 DRC D931 20PR 160/157F TTF карьер',
            '12.00R24 DRC D931 160/157F 20PR TTF карьер',
        ),
    ],
)
def test_stk_tire_compose_glues_in_pioner_order(raw: str, expected: str) -> None:
    """STK: параметры пересобираются в порядок Пионера."""
    assert StkTireCompose().prepare(RowItem({'title': raw})) == expected


def test_stk_tire_compose_uses_manufacturer_for_brand() -> None:
    """Канонический производитель подставляется на место разобранного бренда."""
    row = RowItem(
        {
            'title': '11R22.5 GREENSTONE DR668 146/143L 16PR шашка',
            'manufacturer_name': 'GreenStone',
        },
    )

    assert StkTireCompose().prepare(row) == '11R22.5 GreenStone DR668 146/143L 16PR шашка'


def test_stk_tire_compose_is_idempotent() -> None:
    """Повторная сборка уже собранного названия не меняет результат."""
    strategy = StkTireCompose()
    row = RowItem({'title': 'Автошина 11R22.5 16PR 146/143L GREENSTONE DR668 шашка'})

    once = strategy.prepare(row)
    twice = strategy.prepare(row)

    assert once == twice == '11R22.5 GREENSTONE DR668 146/143L 16PR шашка'


def test_stk_tire_compose_falls_back_to_normalize_for_disk() -> None:
    """Диск не размер шины: работает обычная нормализация размера."""
    row = RowItem({'title': 'Диск стальной YONGZHENG 22,5*11,75 10 26мм ЕТ0 D281 раст.335 (16мм)'})

    assert StkTireCompose().prepare(row) == 'Диск стальной YONGZHENG 22.5x11.75 10 26мм ЕТ0 D281 раст.335 (16мм)'


def test_stk_tire_compose_empty_title_stays_empty() -> None:
    """Пустой title не превращается в заглушку."""
    assert StkTireCompose().prepare(RowItem({})) == ''
