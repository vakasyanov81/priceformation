"""tests for shared markup arithmetic"""

from parsers.base_parser.price_markup import calc_percent, get_markup

_PURCHASE = 1000
_SALE = 1120
_PERCENT = 0.12
_MARKED_UP = 1120


def test_calc_percent() -> None:
    assert calc_percent(_SALE, _PURCHASE) == _PERCENT


def test_get_markup() -> None:
    assert get_markup(_PURCHASE, _PERCENT) == _MARKED_UP
