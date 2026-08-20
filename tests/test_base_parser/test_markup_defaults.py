"""tests for markup fallbacks and missing vendor config."""

from typing import Any

from test_parsers.test_vendors.parse_config import MimMarkupRulesProviderForTests, make_parse_configuration
from test_parsers.test_vendors.test_parse_poshk import VendorListProviderForTests

from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.base_parser_config import BasePriceParseConfigurationParams, ParseConfiguration
from parsers.data_provider.markup_rules import MarkupRulesProviderBase
from parsers.data_provider.vendor_list import VendorParams
from parsers.row_item.row_item import RowItem
from parsers.vendors.pioner import pioner_params

_ZERO = 0
_SOME_PRICE = 1000


class _EmptyMarkupRules(MarkupRulesProviderBase):
    def get_markup_data(self) -> dict[str, Any]:
        return {"markup_rules": {}}


def _parser(config: BasePriceParseConfigurationParams) -> BaseParser:
    return BaseParser(parse_config=ParseConfiguration(config))


def test_markup_percent_empty_map_is_zero() -> None:
    parser = _parser(make_parse_configuration(pioner_params, markup_rules=_EmptyMarkupRules()))
    assert parser.get_markup_percent(_ZERO) == _ZERO
    assert parser.get_markup_percent(_SOME_PRICE) == _ZERO


def test_missing_vendor_is_disabled() -> None:
    config = make_parse_configuration(pioner_params)._replace(vendor_list=VendorListProviderForTests({}))
    parser = _parser(config)
    assert parser.get_current_vendor_config() == VendorParams(enabled=0)
    assert parser.is_active is False


def test_markup_without_prices_is_zero() -> None:
    parser = _parser(make_parse_configuration(pioner_params, markup_rules=MimMarkupRulesProviderForTests()))
    row = RowItem({})
    parser.add_price_markup(row)
    assert row.price_markup == _ZERO
