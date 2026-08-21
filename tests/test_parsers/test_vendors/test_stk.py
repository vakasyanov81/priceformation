"""tests for STK vendor markup logic"""

from typing import Any

import pytest
from test_parsers.test_vendors.parse_config import make_parse_configuration

from parsers.base_parser.base_parser import make_parser
from parsers.base_parser.base_parser_config import ParseConfiguration
from parsers.base_parser.markup_policy import make_map_on_opt_markup_policy
from parsers.data_provider.markup_rules import MarkupRulesProviderBase
from parsers.row_item.row_item import RowItem
from parsers.vendors.stk import STKParser, stk_params

_PRICE_OPT = 1000
_MARKUP = 1060
_LOW_OPT = 500
_LOW_MARKUP = 530
_ROUND_UP_OPT = 1001
_ROUND_UP_MARKUP = 1070
_STORED_PERCENT = 6
_EMPTY_MARKUP = 0


class _StkMarkupRules(MarkupRulesProviderBase):
    def get_markup_data(self) -> dict[str, Any]:
        return {
            "markup_rules": {
                "rule_6": {"min": 0, "max": 999999999, "percent": 0.06},
            }
        }


def _parser() -> STKParser:
    parse_config = ParseConfiguration(make_parse_configuration(stk_params, markup_rules=_StkMarkupRules()))
    return make_parser(
        STKParser,
        parse_config,
        markup_policy=make_map_on_opt_markup_policy(parse_config),
    )


@pytest.mark.parametrize(
    ("price_opt", "markup"),
    [
        (_PRICE_OPT, _MARKUP),
        (_ROUND_UP_OPT, _ROUND_UP_MARKUP),
    ],
)
def test_add_price_markup(price_opt: float, markup: float) -> None:
    """наценка 6% с округлением вверх до десятков"""
    row = RowItem({"price_opt": price_opt})
    _parser().add_price_markup(row)
    assert row.price_markup == markup
    assert row.percent_markup == _STORED_PERCENT


def test_add_price_markup_empty() -> None:
    """без закупочной цены наценка не ставится"""
    row = RowItem({})
    _parser().add_price_markup(row)
    assert row.price_markup == _EMPTY_MARKUP


def test_process_markup_and_rest() -> None:
    """process_parsed_row вызывает skip_by_min_rest и add_price_markup"""
    parser = _parser()
    row_ok = RowItem({"price_opt": _PRICE_OPT, "rest_count": 10})
    row_low = RowItem({"price_opt": _LOW_OPT, "rest_count": 1})

    parser.process_parsed_row(row_ok)
    parser.process_parsed_row(row_low)

    assert row_ok.price_markup == _MARKUP
    assert row_ok.rest_count == 10
    # 0 через дескриптор даёт falsy → None при чтении
    assert row_low.to_dict().get("rest_count") == 0
    assert row_low.price_markup == _LOW_MARKUP
