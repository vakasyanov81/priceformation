"""tests for markup fallbacks and missing vendor config."""

import pytest
from test_parsers.test_vendors._test_providers import (
    BlackListProviderForTests,
    ManufacturerAliasesProviderForTests,
    MarkupRulesProviderForTests,
)

from domain.row_item.row_item import RowItem
from parsers.base_parser.base_parser import BaseParser, make_parser
from parsers.base_parser.base_parser_config import (
    BasePriceParseConfigurationParams,
    ParseConfiguration,
    ParseParamsSupplier,
    ParserParams,
)
from parsers.base_parser.markup_policy import (
    IdentityMarkupPolicy,
    MapOnOptMarkupPolicy,
    MarkupPolicy,
    make_map_on_opt_markup_policy,
)
from parsers.base_parser.row_processor import MarkupPolicyNotSetError
from parsers.data_provider import AbsoluteMarkUpRules, MarkUpRule, MarkupRulesConfig
from parsers.data_provider.markup_rules import MarkupRulesProviderBase

_ZERO = 0
_SOME_PRICE = 1000
_MAP_OPT = 100
_MAP_PERCENT = 0.7
_MAP_PRICE = 170
_MAP_STORED_PERCENT = 70
_IDENTITY_OPT = 1234.56
_EMPTY_RULES_WHERE = 'test_markup_rules.json'


_SUPPLIER = ParseParamsSupplier(folder_name='test', name='Тест', code='99')


def _base_params() -> BasePriceParseConfigurationParams:
    return BasePriceParseConfigurationParams(
        black_list_provider=BlackListProviderForTests(),
        markup_rules_provider=MarkupRulesProviderForTests(),
        manufacturer_aliases=ManufacturerAliasesProviderForTests(),
        parser_params=ParserParams(
            supplier=_SUPPLIER,
            start_row=1,
            sheet_info='',
            columns={},
            stop_words=(),
            file_templates=(),
            sheet_indexes=(),
            row_item_adaptor=RowItem,
        ),
    )


class _EmptyMarkupRules(MarkupRulesProviderBase):
    def get_markup_data(self) -> MarkupRulesConfig:
        return MarkupRulesConfig.from_dict({}, _EMPTY_RULES_WHERE)


def _empty_params() -> BasePriceParseConfigurationParams:
    base = _base_params()
    return BasePriceParseConfigurationParams(
        black_list_provider=base.black_list_provider,
        markup_rules_provider=_EmptyMarkupRules(),
        manufacturer_aliases=base.manufacturer_aliases,
        parser_params=base.parser_params,
    )


def _parser(
    config: BasePriceParseConfigurationParams,
    *,
    markup_policy: MarkupPolicy | None = None,
) -> BaseParser:
    return make_parser(BaseParser, ParseConfiguration(config), markup_policy=markup_policy)


def _map_on_opt_policy() -> MapOnOptMarkupPolicy:
    return MapOnOptMarkupPolicy(
        MarkupRulesConfig(absolute_markup_rules=AbsoluteMarkUpRules()),
        (MarkUpRule(min=0, max=201, percent_markup=_MAP_PERCENT),),
    )


def test_markup_percent_empty_map_is_zero() -> None:
    parser = _parser(_empty_params())
    assert parser.get_markup_percent(_ZERO) == _ZERO
    assert parser.get_markup_percent(_SOME_PRICE) == _ZERO


def test_missing_vendor_is_disabled() -> None:
    """Вендор без _vendor_config считается активным (обратная совместимость)."""
    parser = _parser(_base_params())
    assert parser.is_active is True


def test_markup_without_prices_is_zero() -> None:
    parser = _parser(_base_params())
    row = RowItem({})
    parser.add_price_markup(row)
    assert row.pricing.price_markup == _ZERO


def test_markup_without_policy_raises() -> None:
    parser = BaseParser(parse_config=ParseConfiguration(_base_params()))
    with pytest.raises(MarkupPolicyNotSetError):
        parser.get_markup_percent(_SOME_PRICE)


def test_mim_skips_stored_percent() -> None:
    parser = _parser(_base_params())
    row = RowItem({'price_opt': _SOME_PRICE})
    parser.add_price_markup(row)
    assert row.pricing.percent_markup is None


def test_map_on_opt_stores_percent() -> None:
    parser = _parser(_base_params(), markup_policy=_map_on_opt_policy())
    row = RowItem({'price_opt': _MAP_OPT})
    parser.add_price_markup(row)
    assert row.pricing.price_markup == _MAP_PRICE
    assert row.pricing.percent_markup == _MAP_STORED_PERCENT


def test_make_map_on_opt_markup_policy() -> None:
    policy = make_map_on_opt_markup_policy(ParseConfiguration(_base_params()))
    assert isinstance(policy, MapOnOptMarkupPolicy)


def test_identity_add_price_markup_keeps_opt() -> None:
    parser = _parser(_base_params(), markup_policy=IdentityMarkupPolicy.create())
    row = RowItem({'price_opt': _IDENTITY_OPT})
    parser.add_price_markup(row)
    assert row.pricing.price_markup == _IDENTITY_OPT
    assert row.pricing.percent_markup is None
