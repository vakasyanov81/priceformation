"""tests for row item formatters"""

from typing import Any

import pytest

from parsers.row_item.row_item import RowItem
from parsers.row_item.row_item_formatter import get_try_to_int_or_float, get_try_to_int_or_str


@pytest.mark.parametrize("code, assert_result", [("1", 1), ("1.0", 1), ("1.5", 1.5), ("0.5", 0.5), (None, None)])
def test_try_to_int_or_float(code: Any, assert_result: Any) -> None:
    assert assert_result == get_try_to_int_or_float(code)


def test_try_to_int_or_float_raise_for_str() -> None:
    with pytest.raises(ValueError):
        get_try_to_int_or_float("bar")


@pytest.mark.parametrize("code, assert_result", [("1", 1), ("1.0", 1), ("1.5", "1.5"), ("bar", "bar")])
def test_try_to_int_or_str(code: Any, assert_result: Any) -> None:
    assert assert_result == get_try_to_int_or_str(code)


def test_row_item_price_opt() -> None:
    row = RowItem({"price_opt": "10"})
    assert 10 == row.price_opt
    row.price_opt = "50 руб."
    assert 50 == row.price_opt
