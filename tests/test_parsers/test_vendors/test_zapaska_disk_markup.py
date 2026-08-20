"""tests for zapaska disk markup helpers."""

import pytest

from parsers.vendors.zapaska_disk_markup import (
    MIN_RECOMMENDED_MARGIN_PERCENT,
    _get_price_percent_markup,
    _is_small_recommended_price,
    _make_price_recommended_markup,
    make_absolute_markup,
)

_OPT = 1000
_ENOUGH_RECOMMENDED = 2000
_EXACT_EIGHT_PERCENT = 1080
_ABOVE_EIGHT_PERCENT = 1081
_SMALL_MARGIN_PRICE = 1100
_LARGE_MARGIN_PRICE = 1300
_ABSOLUTE_FLOOR = 1150


@pytest.mark.parametrize(
    ("price_opt", "percent"),
    [
        (0, 0.22),
        (4999, 0.22),
        (5000, 0.20),
        (9999, 0.20),
        (10000, 0.16),
        (14999, 0.16),
        (15000, 0.14),
        (19999, 0.14),
        (20000, 0.12),
        (24999, 0.12),
        (25000, 0.12),
    ],
)
def test_price_percent_markup_by_range(price_opt: float, percent: float) -> None:
    assert _get_price_percent_markup(price_opt) == pytest.approx(percent)


def test_absolute_markup_small_margin() -> None:
    assert make_absolute_markup(_SMALL_MARGIN_PRICE, _OPT) == _ABSOLUTE_FLOOR


def test_absolute_markup_at_delta() -> None:
    assert make_absolute_markup(_ABSOLUTE_FLOOR, _OPT) == _ABSOLUTE_FLOOR


def test_absolute_markup_keeps_price() -> None:
    assert make_absolute_markup(_LARGE_MARGIN_PRICE, _OPT) == _LARGE_MARGIN_PRICE


def test_small_recommended_at_threshold() -> None:
    assert _is_small_recommended_price(_EXACT_EIGHT_PERCENT, _OPT, MIN_RECOMMENDED_MARGIN_PERCENT) is True


def test_small_recommended_above_limit() -> None:
    assert _is_small_recommended_price(_ABOVE_EIGHT_PERCENT, _OPT, MIN_RECOMMENDED_MARGIN_PERCENT) is False


def test_recommended_markup_keeps_percent() -> None:
    price, percent = _make_price_recommended_markup(_ENOUGH_RECOMMENDED, _OPT)
    assert price == _ENOUGH_RECOMMENDED
    assert percent == 1
