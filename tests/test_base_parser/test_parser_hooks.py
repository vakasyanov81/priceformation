"""Default vendor-row pipeline after enrich."""

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
from parsers.base_parser.markup_policy import IdentityMarkupPolicy

_OPT = 100
_REST_OK = 10
_REST_LOW = 1
_CATEGORY = 'Диск'

_CALLS: list[str] = []


class _OrderParser(BaseParser):
    def after_row_mapped(self, row_item: RowItem) -> None:
        _CALLS.append('after')

    def skip_by_min_rest(self, row_item: RowItem) -> None:
        _CALLS.append('skip')
        super().skip_by_min_rest(row_item)

    def category_for(self, row_item: RowItem) -> str | None:
        _CALLS.append('category')
        return _CATEGORY


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


def _reset_calls() -> None:
    _CALLS.clear()


def _make_parser(*, markup_policy: IdentityMarkupPolicy | None = None) -> BaseParser:
    if markup_policy is None:
        markup_policy = IdentityMarkupPolicy.create()
    parse_config = ParseConfiguration(_base_params())
    return make_parser(
        _OrderParser,
        parse_config,
        markup_policy=markup_policy,
    )


def test_hook_order_after_enrich() -> None:
    """after_row_mapped → skip_by_min_rest → apply_category → add_price_markup."""
    parser = _make_parser()
    row = RowItem({'title': '205/55R16', 'price_opt': _OPT, 'rest_count': _REST_OK})
    row.set_field('type_production', _CATEGORY)

    _reset_calls()
    parser.apply_vendor_hooks([row])

    assert _CALLS == ['after', 'skip', 'category']
    assert row.identity.title == '205/55R16'


def test_rest_filter_drops_low_rest() -> None:
    """skip_by_min_rest обнуляет остаток при малом значении."""
    parser = _make_parser()
    row = RowItem({'price_opt': _OPT, 'rest_count': _REST_LOW})

    _reset_calls()
    parser.apply_vendor_hooks([row])

    assert row.stock.rest_count == 0
    assert row.pricing.price_markup == _OPT


def test_title_not_overwritten_by_default() -> None:
    """Default title strategy не меняет title."""
    parser = _make_parser()
    row = RowItem({'title': '205/55R16', 'price_opt': _OPT, 'rest_count': _REST_OK})

    _reset_calls()
    parser.set_prepared_title(row)

    assert row.identity.title == '205/55R16'


def test_deprecated_vendor_config_fallback_active() -> None:
    """ParseConfiguration без _vendor_config не падает (обратная совместимость)."""
    parser = _make_parser()
    assert parser.is_active is True
