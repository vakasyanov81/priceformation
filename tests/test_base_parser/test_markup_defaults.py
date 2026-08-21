"""tests for markup fallbacks and missing vendor config."""

from typing import Any

import pytest
from test_parsers.test_vendors.parse_config import MimMarkupRulesProviderForTests, make_parse_configuration
from test_parsers.test_vendors.test_parse_poshk import VendorListProviderForTests

from parsers.base_parser.base_parser import BaseParser, MarkupPolicyNotSetError, make_parser
from parsers.base_parser.base_parser_config import BasePriceParseConfigurationParams, ParseConfiguration
from parsers.base_parser.markup_policy import MapOnOptMarkupPolicy, MarkupPolicy, make_map_on_opt_markup_policy
from parsers.data_provider.markup_rules import AbsoluteMarkUpRules, MarkUpParams, MarkupRules, MarkupRulesProviderBase
from parsers.data_provider.vendor_list import VendorParams
from parsers.row_item.row_item import RowItem
from parsers.vendors.pioner import pioner_params

_ZERO = 0
_SOME_PRICE = 1000
_MAP_OPT = 100
_MAP_PERCENT = 0.7
_MAP_PRICE = 170
_MAP_STORED_PERCENT = 70


class _EmptyMarkupRules(MarkupRulesProviderBase):
    def get_markup_data(self) -> dict[str, Any]:
        return {"markup_rules": {}}


def _parser(
    config: BasePriceParseConfigurationParams,
    *,
    markup_policy: MarkupPolicy | None = None,
) -> BaseParser:
    return make_parser(BaseParser, ParseConfiguration(config), markup_policy=markup_policy)


def _map_on_opt_policy() -> MapOnOptMarkupPolicy:
    return MapOnOptMarkupPolicy(
        MarkupRules(
            markup_rules={},
            absolute_markup_rules=AbsoluteMarkUpRules(),
        ),
        (MarkUpParams(min=0, max=201, percent_markup=_MAP_PERCENT),),
    )


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


def test_markup_without_policy_raises() -> None:
    parser = BaseParser(parse_config=ParseConfiguration(make_parse_configuration(pioner_params)))
    with pytest.raises(MarkupPolicyNotSetError):
        parser.get_markup_percent(_SOME_PRICE)


def test_mim_skips_stored_percent() -> None:
    parser = _parser(make_parse_configuration(pioner_params, markup_rules=MimMarkupRulesProviderForTests()))
    row = RowItem({"price_opt": _SOME_PRICE})
    parser.add_price_markup(row)
    assert row.percent_markup is None


def test_map_on_opt_stores_percent() -> None:
    parser = _parser(make_parse_configuration(pioner_params), markup_policy=_map_on_opt_policy())
    row = RowItem({"price_opt": _MAP_OPT})
    parser.add_price_markup(row)
    assert row.price_markup == _MAP_PRICE
    assert row.percent_markup == _MAP_STORED_PERCENT


def test_make_map_on_opt_markup_policy() -> None:
    policy = make_map_on_opt_markup_policy(ParseConfiguration(make_parse_configuration(pioner_params)))
    assert isinstance(policy, MapOnOptMarkupPolicy)
