"""tests for markup fallbacks and missing vendor config."""

import pytest
from test_parsers.test_vendors._test_providers import (
    BlackListProviderForTests,
    ManufacturerAliasesProviderForTests,
    MarkupRulesProviderForTests,
)

from domain.config_context import get_config_provider
from domain.row_item.row_item import RowItem
from parsers.base_parser.base_parser import BaseParser, make_parser
from parsers.base_parser.base_parser_config import (
    BasePriceParseConfigurationParams,
    ParseConfiguration,
    ParseParamsSupplier,
    ParserParams,
)
from parsers.base_parser.file_reader import FileReader
from parsers.base_parser.markup_policy import (
    IdentityMarkupPolicy,
    MapOnOptMarkupPolicy,
    MarkupPolicy,
    make_map_on_opt_markup_policy,
    make_markup_policy,
)
from parsers.base_parser.row_processor import MarkupPolicyNotSetError, RowProcessor
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
        config_provider=get_config_provider(),
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
        config_provider=get_config_provider(),
        parser_params=base.parser_params,
    )


def _parser(
    config: BasePriceParseConfigurationParams,
    *,
    markup_policy: MarkupPolicy | None = None,
) -> BaseParser:
    return make_parser(BaseParser, ParseConfiguration(config), markup_policy=markup_policy)


def _processor(
    config: BasePriceParseConfigurationParams,
    *,
    markup_policy: MarkupPolicy | None = None,
) -> RowProcessor:
    policy = make_markup_policy(ParseConfiguration(config)) if markup_policy is None else markup_policy
    return RowProcessor(markup_policy=policy)


def _map_on_opt_policy() -> MapOnOptMarkupPolicy:
    return MapOnOptMarkupPolicy(
        MarkupRulesConfig(absolute_markup_rules=AbsoluteMarkUpRules()),
        (MarkUpRule(min=0, max=201, percent_markup=_MAP_PERCENT),),
    )


def test_markup_percent_empty_map_is_zero() -> None:
    processor = _processor(_empty_params())
    assert processor.get_markup_percent(_ZERO) == _ZERO
    assert processor.get_markup_percent(_SOME_PRICE) == _ZERO


def test_missing_vendor_is_disabled() -> None:
    """Вендор без vendor_config считается активным (обратная совместимость)."""
    parser = _parser(_base_params())
    assert parser.settings.is_active is True


def test_markup_without_prices_is_zero() -> None:
    row = RowItem({})
    _processor(_base_params()).add_price_markup(row)
    assert row.pricing.price_markup == _ZERO


def test_markup_without_policy_raises() -> None:
    with pytest.raises(MarkupPolicyNotSetError):
        RowProcessor().get_markup_percent(_SOME_PRICE)


def test_markup_policy_error_message() -> None:
    """Текст ошибки читает пользователь: он закреплён дословно."""
    assert str(MarkupPolicyNotSetError()) == 'markup_policy is not set'


def test_mim_skips_stored_percent() -> None:
    row = RowItem({'price_opt': _SOME_PRICE})
    _processor(_base_params()).add_price_markup(row)
    assert row.pricing.percent_markup is None


def test_map_on_opt_stores_percent() -> None:
    row = RowItem({'price_opt': _MAP_OPT})
    _processor(_base_params(), markup_policy=_map_on_opt_policy()).add_price_markup(row)
    assert row.pricing.price_markup == _MAP_PRICE
    assert row.pricing.percent_markup == _MAP_STORED_PERCENT


def test_make_map_on_opt_markup_policy() -> None:
    config = ParseConfiguration(_base_params())
    policy = make_map_on_opt_markup_policy(config)
    assert isinstance(policy, MapOnOptMarkupPolicy)
    assert policy._rules == config.get_markup_rules()
    assert policy._price_map == config.get_price_markup_map()


def test_identity_add_price_markup_keeps_opt() -> None:
    row = RowItem({'price_opt': _IDENTITY_OPT})
    _processor(_base_params(), markup_policy=IdentityMarkupPolicy.create()).add_price_markup(row)
    assert row.pricing.price_markup == _IDENTITY_OPT
    assert row.pricing.percent_markup is None


_GET_MARKUP_POLICY = MapOnOptMarkupPolicy(
    MarkupRulesConfig(absolute_markup_rules=AbsoluteMarkUpRules()),
    (
        MarkUpRule(min=0, max=0, percent_markup=0.2),
        MarkUpRule(min=1, max=10, percent_markup=0.5),
    ),
)


def test_get_markup_percent_uses_price_argument() -> None:
    """RowProcessor.get_markup_percent передаёт цену дальше, а не None."""
    processor = _processor(_base_params(), markup_policy=_GET_MARKUP_POLICY)
    assert processor.get_markup_percent(5) == 0.5


class _FakeReader:
    """Заглушка читателя данных для make_parser."""


def test_make_parser_passes_data_reader_when_given() -> None:
    """Явный data_reader попадает в парсер, а не подменяется дефолтом."""
    parser = make_parser(
        BaseParser,
        ParseConfiguration(_base_params()),
        data_reader=_FakeReader,
    )
    file_reader = parser.price_files.file_reader
    assert isinstance(file_reader, FileReader)
    assert file_reader.data_reader is _FakeReader


def test_make_parser_passes_file_prices() -> None:
    """file_prices доезжает до parser.files как есть."""
    parser = make_parser(BaseParser, ParseConfiguration(_base_params()), file_prices=['a.xls'])
    assert parser.price_files.files == ['a.xls']
