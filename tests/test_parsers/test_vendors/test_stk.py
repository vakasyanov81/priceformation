"""tests for STK vendor markup logic"""

from unittest.mock import patch

from parsers.row_item.row_item import RowItem
from parsers.vendors.stk import STKParser

_PRICE_OPT = 1000
_MARKUP = 1060
_LOW_OPT = 500
_LOW_MARKUP = 530


def test_add_price_markup():
    """наценка 6% с округлением вверх до десятков"""
    parser = object.__new__(STKParser)
    row = RowItem({"price_opt": _PRICE_OPT})
    parser.add_price_markup(row)
    assert row.price_markup == _MARKUP


def test_add_price_markup_empty():
    """без закупочной цены наценка не ставится"""
    parser = object.__new__(STKParser)
    row = RowItem({})
    parser.add_price_markup(row)
    assert row.price_markup == 0


def test_process_markup_and_rest():
    """process вызывает skip_by_min_rest и add_price_markup"""
    parser = object.__new__(STKParser)
    row_ok = RowItem({"price_opt": _PRICE_OPT, "rest_count": 10})
    row_low = RowItem({"price_opt": _LOW_OPT, "rest_count": 1})
    parser.result = [row_ok, row_low]

    with patch("parsers.vendors.stk.BaseParser.process", return_value=parser.result):
        assert parser.process() == parser.result

    assert row_ok.price_markup == _MARKUP
    assert row_ok.rest_count == 10
    # 0 через дескриптор даёт falsy → None при чтении
    assert row_low.to_dict().get("rest_count") == 0
    assert row_low.price_markup == _LOW_MARKUP
