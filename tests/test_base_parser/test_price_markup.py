"""tests for shared markup arithmetic"""

import pytest

from domain.row_item.row_item import RowItem
from parsers.base_parser.price_markup import calc_percent, fill_percent_markup, get_markup, recommended_percent

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
