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
from parsers.base_parser.protocols import RowProcessorProtocol
from parsers.base_parser.row_filters import drop_empty_rest
from parsers.base_parser.row_pipeline import RowPipeline, make_row_pipeline
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
    settings = ParserSettings(parse_config)
    stats = ParserStats()
    return TireAndDiskHandler(
        settings=settings, stats=stats, pipeline=make_row_pipeline(settings, stats, strategy_hooks, row_processor)
    )


class TireAndDiskHandler:
    """Реализация группы: модель, стратегии, pipeline и выходные поля."""

    product_group: Literal[ProductGroup.TIRE_AND_DISK] = ProductGroup.TIRE_AND_DISK

    def __init__(
        self,
        *,
        settings: ParserSettings,
        stats: ParserStats | None = None,
        pipeline: RowPipeline | None = None,
        grouper_factory: Callable[[list[RowItem]], CommonPriceGrouper] | None = None,
    ) -> None:
        self.settings = settings
        self.stats = stats or ParserStats()
        self._pipeline = make_row_pipeline(settings, self.stats) if pipeline is None else pipeline
        self._grouper_factory = grouper_factory or CommonPriceGrouper

    @property
    def pipeline(self) -> RowPipeline:
        """Граф собирается один раз; зависимости pipeline нельзя заменить по отдельности."""
        return self._pipeline

    def create_position(self, fields: InputFields) -> RowItem:
        return RowItem(dict(fields))

    def process_rows(self, positions: Sequence[RowItem]) -> list[RowItem]:
        """Выполнить фильтры, обогащение и шаги pipeline до финальной наценки."""
        row_items = self.pipeline.row_filters.filter_warehouses(list(positions))
        row_items = self.pipeline.enricher.keep(row_items)
        row_items = self.pipeline.enricher.enrich(row_items)
        self.pipeline.run(row_items)
        return row_items

    def process(self, positions: Sequence[RowItem]) -> TireAndDiskResult:
        """Обработать строки секции: сбросить кэш категорий, прогнать фильтры и завершить расчёт."""
        categories = self.pipeline.enricher.categories
        categories.lookup.reset()
        return TireAndDiskResult(tuple(finish_processing(self.process_rows(positions), self.stats)))

    def group(self, package: ProductGroupResult[RowItem]) -> TireAndDiskResult:
        grouper = self._grouper_factory(list(package.positions))
        return TireAndDiskResult(tuple(grouper.group_by_params().get_row_items()))

    def prepare_output(self, package: ProductGroupResult[RowItem]) -> tuple[OutputFields, ...]:
        return tuple(position.to_dict() for position in package.positions)
