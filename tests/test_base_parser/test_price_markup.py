"""tests for shared markup arithmetic"""

import pytest

from domain.row_item.row_item import RowItem
from parsers.base_parser.price_markup import (
    calc_percent,
    fill_absolute_markup,
    fill_percent_markup,
    get_markup,
    recommended_percent,
)

_PURCHASE = 1000
_SALE = 1120
_PERCENT = 0.12
_MARKED_UP = 1120


def test_calc_percent() -> None:
    assert calc_percent(_SALE, _PURCHASE) == _PERCENT


def test_get_markup() -> None:
    assert get_markup(_PURCHASE, _PERCENT) == _MARKED_UP


def test_recommended_percent_zero_purchase_price_raises() -> None:
    """Закуп 0 при заданной РРЦ — деление на ноль, а не подмена закупа единицей."""
    with pytest.raises(ZeroDivisionError):
        recommended_percent(0, 100)


def test_fill_percent_markup_rounds_to_hundredths() -> None:
    """Процент округляется до сотых, а не до целого и не до тысячных."""
    row = RowItem({'price_opt': 3, 'price_markup': 4})

    fill_percent_markup([row])

    assert row.pricing.percent_markup == 33.33


def test_fill_absolute_markup_subtracts_purchase() -> None:
    """Абсолютная наценка — отпускная минус закуп."""
    row = RowItem({'price_opt': 1000, 'price_markup': 1120})

    fill_absolute_markup([row])

    assert row.pricing.absolute_markup == 120


def test_fill_absolute_markup_skips_without_markup_price() -> None:
    """Без цены с наценкой абсолютная наценка не считается."""
    row = RowItem({'price_opt': 1000})

    fill_absolute_markup([row])

    assert row.pricing.absolute_markup == 0


def test_fill_absolute_markup_continues_after_row_without_markup() -> None:
    """Строка без цены с наценкой не прерывает обход: следующая считается."""
    without_markup = RowItem({'price_opt': 1000})
    rows = [without_markup, RowItem({'price_opt': 1000, 'price_markup': 1120})]

    fill_absolute_markup(rows)

    assert [row.pricing.absolute_markup for row in rows] == [0, 120]


def test_fill_absolute_markup_rounds_to_cents() -> None:
    """Абсолютная наценка округляется до копеек."""
    row = RowItem({'price_opt': 33.333, 'price_markup': 100})

    fill_absolute_markup([row])

    assert row.pricing.absolute_markup == 66.67
