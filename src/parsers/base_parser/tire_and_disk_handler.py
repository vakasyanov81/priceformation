"""Обработка группы шин и дисков на существующих коллабораторах разбора."""

from collections.abc import Callable, Sequence
from typing import Literal

from domain.product_group_handler import InputFields, OutputFields
from domain.product_group_result import ProductGroupResult, TireAndDiskResult
from domain.product_groups import ProductGroup
from domain.row_item.row_item import RowItem
from parsers.base_parser.base_parser_config import ParseConfiguration
from parsers.base_parser.parse_statistic import ParserStats
from parsers.base_parser.parser_settings import ParserSettings
from parsers.base_parser.price_markup import fill_absolute_markup, fill_percent_markup
from parsers.base_parser.protocols import RowProcessorProtocol, TitleFilterProtocol
from parsers.base_parser.row_enricher import make_row_enricher
from parsers.base_parser.row_filters import RowFilters, drop_empty_rest
from parsers.base_parser.row_pipeline import RowPipeline
from parsers.base_parser.row_processor import RowProcessor
from parsers.base_parser.strategy_hooks import StrategyHooks
from parsers.common_price.grouper import CommonPriceGrouper


def count_type_corrections(positions: Sequence[RowItem]) -> int:
    return sum(1 for row_item in positions if row_item.vendor.type_corrected)


def finish_processing(positions: Sequence[RowItem], stats: ParserStats) -> list[RowItem]:
    row_items = drop_empty_rest(list(positions))
    fill_percent_markup(row_items)
    fill_absolute_markup(row_items)
    stats.type_corrections = count_type_corrections(row_items)
    stats.title_conflicts = sum(1 for row_item in row_items if row_item.vendor.title_conflict)
    stats.titles_not_composed = sum(1 for row_item in row_items if row_item.vendor.title_not_composed)
    return row_items


def make_handler(
    parse_config: ParseConfiguration,
    *,
    row_processor: RowProcessorProtocol,
    strategy_hooks: StrategyHooks,
) -> TireAndDiskHandler:
    return TireAndDiskHandler(
        settings=ParserSettings(parse_config), row_processor=row_processor, strategy_hooks=strategy_hooks
    )


class TireAndDiskHandler:
    """Реализация группы: модель, стратегии, pipeline и выходные поля."""

    def __init__(
        self,
        *,
        settings: ParserSettings,
        stats: ParserStats | None = None,
        row_processor: RowProcessorProtocol | None = None,
        title_filter: TitleFilterProtocol | None = None,
        strategy_hooks: StrategyHooks | None = None,
        grouper_factory: Callable[[list[RowItem]], CommonPriceGrouper] | None = None,
    ) -> None:
        self.settings = settings
        self.stats = stats or ParserStats()
        self.row_filters = RowFilters(strategy_hooks)
        self.enricher = make_row_enricher(self.settings, self.stats, strategy_hooks, title_filter)
        self.pipeline = RowPipeline(strategy_hooks, self.row_filters, self.enricher, row_processor or RowProcessor())
        self._grouper_factory = grouper_factory or CommonPriceGrouper

    @property
    def product_group(self) -> Literal[ProductGroup.TIRE_AND_DISK]:
        return ProductGroup.TIRE_AND_DISK

    def create_position(self, fields: InputFields) -> RowItem:
        return RowItem(dict(fields))

    def process_rows(self, positions: Sequence[RowItem]) -> list[RowItem]:
        """Выполнить фильтры, обогащение и шаги pipeline до финальной наценки."""
        row_items = self.row_filters.filter_warehouses(list(positions))
        row_items = self.enricher.keep(row_items)
        row_items = self.enricher.enrich(row_items)
        self.pipeline.run(row_items)
        return row_items

    def process(self, positions: Sequence[RowItem]) -> TireAndDiskResult:
        return TireAndDiskResult(tuple(finish_processing(self.process_rows(positions), self.stats)))

    def group(self, package: ProductGroupResult[RowItem]) -> TireAndDiskResult:
        grouper = self._grouper_factory(list(package.positions))
        return TireAndDiskResult(tuple(grouper.group_by_params().get_row_items()))

    def prepare_output(self, package: ProductGroupResult[RowItem]) -> tuple[OutputFields, ...]:
        return tuple(position.to_dict() for position in package.positions)
