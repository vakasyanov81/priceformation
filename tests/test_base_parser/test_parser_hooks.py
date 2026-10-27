"""Default vendor-row pipeline after enrich."""

from unittest.mock import MagicMock

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
from parsers.base_parser.category_service import CategoryLookup, CategoryService
from parsers.base_parser.markup_policy import IdentityMarkupPolicy
from parsers.base_parser.row_filters import RowFilters
from parsers.base_parser.strategy_hooks import StrategyHooks
from parsers.base_parser.title_service import TitleService

_OPT = 100
_REST_OK = 10
_REST_LOW = 1
_CATEGORY = 'Диск'

_CALLS: list[str] = []


class _SpyRowFilters(RowFilters):
    def skip_by_min_rest(self, row_item: RowItem) -> None:
        _CALLS.append('skip')
        super().skip_by_min_rest(row_item)


class _SpyCategories(CategoryService):
    def category_for(self, row_item: RowItem) -> str | None:
        _CALLS.append('category')
        return _CATEGORY


class _RebuildTitles(TitleService):
    """Название собирается заново и не несёт в себе ни года, ни уценки."""

    def get_prepared_title(self, row_item: RowItem) -> str | None:
        return '175/65R14 Viatti Brina V-521 82T'


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
    parser = make_parser(
        BaseParser,
        parse_config,
        markup_policy=markup_policy,
    )
    parser.pipeline.row_filters = _SpyRowFilters()
    parser.enricher.categories = _SpyCategories(None, CategoryLookup(parser.stats))
    return parser


def test_hook_order_after_enrich() -> None:
    """skip_by_min_rest → apply_category → add_price_markup."""
    parser = _make_parser()
    row = RowItem({'title': '205/55R16', 'price_opt': _OPT, 'rest_count': _REST_OK})
    row.set_field('type_production', _CATEGORY)

    _reset_calls()
    parser.pipeline.run([row])

    assert _CALLS == ['skip', 'category']
    assert row.identity.title == '205/55R16'


def test_rest_filter_drops_low_rest() -> None:
    """skip_by_min_rest обнуляет остаток при малом значении."""
    parser = _make_parser()
    row = RowItem({'price_opt': _OPT, 'rest_count': _REST_LOW})

    _reset_calls()
    parser.pipeline.run([row])

    assert row.stock.rest_count == 0
    assert row.pricing.price_markup == _OPT


def test_title_not_overwritten_by_default() -> None:
    """Default title strategy не меняет title."""
    parser = _make_parser()
    row = RowItem({'title': '205/55R16', 'price_opt': _OPT, 'rest_count': _REST_OK})

    _reset_calls()
    parser.enricher.titles.set_prepared_title(row)

    assert row.identity.title == '205/55R16'


def test_markdown_title_marks_row_down() -> None:
    """«Уценка» в названии ставит признак уценки; обычное название признак не трогает."""
    parser = _make_parser()
    marked = RowItem({'title': '13 Trebl 5.0*13 паллета Уценка Дефект ЛКП', 'price_opt': _OPT})
    regular = RowItem({'title': '13 Trebl 5.0*13 паллета', 'price_opt': _OPT})

    parser.enricher.titles.set_prepared_title(marked)
    parser.enricher.titles.set_prepared_title(regular)

    assert marked.stock.marked_down is True
    assert regular.stock.marked_down is None


def test_production_year_is_taken_from_title() -> None:
    """Год выпуска из названия попадает в поле, без года поле пустое."""
    parser = _make_parser()
    dated = RowItem({'title': '175/65R14 Viatti Brina V-521 82T 2023г.в.', 'price_opt': _OPT})
    undated = RowItem({'title': '175/65R14 Viatti Brina V-521 82T', 'price_opt': _OPT})

    parser.enricher.titles.set_prepared_title(dated)
    parser.enricher.titles.set_prepared_title(undated)

    assert dated.stock.production_year == 2023
    assert undated.stock.production_year is None


def _make_rebuild_parser() -> BaseParser:
    parser = _make_parser()
    parser.enricher.titles = _RebuildTitles(None, parser.enricher.titles.title_filter)
    return parser


def test_production_year_survives_rebuilt_title() -> None:
    """Собранное название года выпуска не несёт: год берётся из текста поставщика до сборки."""
    row = RowItem({'title': '175/65R14 Viatti Brina V-521 82T 2023г.в.', 'price_opt': _OPT})

    _make_rebuild_parser().enricher.titles.set_prepared_title(row)

    assert row.identity.title == '175/65R14 Viatti Brina V-521 82T'
    assert row.stock.production_year == 2023


def test_production_plant_survives_rebuilt_title() -> None:
    """Завод берётся из текста поставщика до сборки: собранное название его не несёт."""
    row = RowItem({'title': '175/65R14 Viatti Brina V-521 82T НкШЗ', 'price_opt': _OPT})

    _make_rebuild_parser().enricher.titles.set_prepared_title(row)

    assert row.identity.title == '175/65R14 Viatti Brina V-521 82T'
    assert row.stock.production_plant == 'НкШЗ'


def test_markdown_survives_rebuilt_title() -> None:
    """Собранное название слова «Уценка» не несёт: признак уценки берётся из текста поставщика до сборки."""
    row = RowItem({'title': '175/65R14 Viatti Brina V-521 82T Уценка', 'price_opt': _OPT})

    _make_rebuild_parser().enricher.titles.set_prepared_title(row)

    assert row.stock.marked_down is True


def test_deprecated_vendor_config_fallback_active() -> None:
    """ParseConfiguration без vendor_config не падает (обратная совместимость)."""
    parser = _make_parser()
    assert parser.settings.is_active is True


def test_skip_by_min_rest_keeps_large_rest() -> None:
    """Дефолтный путь берёт остаток из строки, а не None."""
    parser = _make_parser()
    row = RowItem({'price_opt': _OPT, 'rest_count': _REST_OK})
    parser.row_filters.skip_by_min_rest(row)
    assert row.stock.rest_count == _REST_OK


def test_set_prepared_title_reports_unchanged_title() -> None:
    """set_prepared_title возвращает True, когда title не изменился."""
    parser = _make_parser()
    row = RowItem({'title': '205/55R16'})
    assert parser.enricher.titles.set_prepared_title(row) is True


def test_pipeline_min_rest_step_runs_rest_strategy() -> None:
    """Шаг 'min_rest' в pipeline распознаётся и применяет стратегию остатка."""
    strategy = MagicMock()
    strategy.item_rest.return_value = _REST_LOW
    hooks = StrategyHooks(rest=strategy, min_rest=4, pipeline=('min_rest',))
    parser = BaseParser(parse_config=ParseConfiguration(_base_params()), strategy_hooks=hooks)

    row = RowItem({'rest_count': _REST_LOW})
    parser.pipeline.process_row(row)

    strategy.item_rest.assert_called_once_with(row)
    assert row.stock.rest_count == 0
