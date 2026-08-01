"""tests for row item boolean field"""

import pytest

from parsers.row_item.row_item import RowItem
from parsers.row_item.row_item_casts import (
    get_integer,
    get_try_to_int_or_float,
)


def test_get_try_to_int_or_float() -> None:
    """Try cast string to int or float"""
    with pytest.raises(ValueError):
        get_try_to_int_or_float("invalid value")
    assert 10 == get_try_to_int_or_float("10")
    assert 10 == get_try_to_int_or_float("10.0")
    assert 10.5 == get_try_to_int_or_float("10.5")


def test_get_integer() -> None:
    """Try cast string to int"""
    with pytest.raises(ValueError):
        get_integer("invalid value")
    assert 10 == get_integer("10")
    assert 10 == get_integer("10.0")
    assert 10 == get_integer("10.5")


def test_row_item_set_boolean() -> None:
    """boolean field accepts True"""
    row = RowItem()
    # row = RowItem({'double_candidate': False})
    row.double_candidate = True
