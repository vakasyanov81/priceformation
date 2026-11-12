"""Оркестрация парсинга прайс-листов поставщиков и группировки.

Сервис заменяет бывший ``CommonPrice``: разбирает прайсы всех (или одного)
поставщиков, собирает статистику пропусков и группирует результат.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Mapping, Sequence
from typing import Any, Protocol

from domain.product_groups import ProductGroup
from domain.row_item.row_item import RowItem
from infrastructure.logging.file_logging import clear_log_files
from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.base_parser_config import ParseConfiguration
from parsers.base_parser.supplier_parser import SupplierParser
from parsers.common_price.grouper import CommonPriceGrouper
from parsers.data_provider.manufacturer_aliases import clear_manufacturer_aliases_cache
from services.group_processing import group_packages
from services.parse_logging import LogMessage, log_parse_failure, parser_messages, skips_messages
from services.parse_result import ParseResult, ParseSelection
from services.parse_statistics import GroupStatistics, UnknownCategorySkip
from services.vendor_source import VendorSource

logger = logging.getLogger(__name__)

type VendorList = Sequence[tuple[type[BaseParser], ParseConfiguration | None]]


class ParserFactory(Protocol):
    """Фабрика вендорного парсера: класс и конфиг → экземпляр."""

    def __call__(
        self,
        parser_cls: type[BaseParser],
        parse_config: ParseConfiguration | None,
    ) -> SupplierParser:
        """Собрать парсер поставщика."""
        ...


class GrouperFactory(Protocol):
    """Фабрика группировщика: записи прайса → CommonPriceGrouper."""

    def __call__(
        self,
        row_items: list[RowItem],
        *,
        aliases_map: dict[str, Any],
        reference_priority: Mapping[str, int],
    ) -> CommonPriceGrouper:
        """Создать группировщик для списка записей с очередью поставщиков-эталонов названия."""
        ...


class ParseOrchestrator:
    """Парсит прайс-листы поставщиков и группирует результат."""

    def __init__(
        self,
        *,
        parser_factory: ParserFactory,
        grouper_factory: GrouperFactory,
        vendor_source: VendorSource,
    ) -> None:
        self._parser_factory = parser_factory
        self._grouper_factory = grouper_factory
        self._vendor_source = vendor_source

    def parse_all(self, vendors: VendorList | None = None, *, selection: ParseSelection | None = None) -> ParseResult:
        """Парсит всех поставщиков (или переданный список) и группирует."""
        if selection is not None:
            selection.groups = ()
        selected = self._vendor_source.all() if vendors is None else vendors
        if selection is not None:
            selection.groups = tuple(
                dict.fromkeys(
                    ProductGroup.TIRE_AND_DISK if config is None else config.product_group or ProductGroup.TIRE_AND_DISK
                    for _, config in selected
                )
            )
        return self._parse_vendors(selected)

    def parse_vendor(self, code: str) -> ParseResult:
        """Парсит одного поставщика по коду реестра и группирует."""
        return self._parse_vendors([self._vendor_source.entry_for(code)])

    def _parse_vendors(self, vendors: VendorList) -> ParseResult:
        """Общий цикл разбора списка поставщиков с итоговой группировкой."""
        parse_result = ParseResult()
        clear_log_files()
        start_time = time.monotonic()
        logger.info('\n============== Начало разбора прайсов =================\n')
        self._parse_all_vendors(parse_result, vendors)
        _emit(skips_messages(parse_result))
        clear_manufacturer_aliases_cache()
        self._group_packages(parse_result)
        elapsed = time.monotonic() - start_time
        logger.info(f'\n===== Окончание разбора прайсов ({elapsed:.2f} сек) ========\n')
        return parse_result

    def _group_packages(self, parse_result: ParseResult) -> None:
        """Передать пакеты обработке собственных моделей."""
        group_packages(parse_result, self._grouper_factory, self._vendor_source, logger)

    def _parse_all_vendors(self, parse_result: ParseResult, vendors: VendorList) -> None:
        """Собрать все группы и стратегии до чтения первого прайса, затем разобрать поставщиков."""
        parsers = [self._parser_factory(vendor_cls, vendor_config) for vendor_cls, vendor_config in vendors]
        for parser in parsers:
            self._parse_supplier(parse_result, parser)
        parse_result.unrouted_rows = _unrouted_rows(vendors)

    def _parse_supplier(self, parse_result: ParseResult, parser: SupplierParser) -> None:
        """Парсит прайс одного поставщика и добавляет пакет его группы к результату."""
        try:
            parsed = parser.parse()
        except Exception as exc:
            log_parse_failure(logger, parser, exc)
            raise
        else:
            parse_result.add_package(parsed)
            counters = parse_result.statistics.setdefault(parsed.product_group, GroupStatistics())
            counters.black_list_skips += parser.stats.black_list_skips
            if parsed.product_group is ProductGroup.TIRE_AND_DISK:
                parse_result.tire_and_disk_diagnostics.accumulate(parser.stats, _parser_unknown_skips(parser))
            _emit(parser_messages(parser, parsed.product_group))


def _emit(messages: list[LogMessage]) -> None:
    """Записать сообщения сводки в лог оркестратора."""
    for level, text in messages:
        logger.log(level, text)


def _parser_unknown_skips(parser: SupplierParser) -> list[UnknownCategorySkip]:
    """Пропуски неизвестных категорий парсера с именем поставщика."""
    skips = parser.stats.unknown_category_skips
    if not skips:
        return []
    supplier = parser.settings.parser_params().supplier.name
    return [(supplier, category) for category in skips]


def _unrouted_rows(vendors: VendorList) -> int:
    """Общий маршрут нескольких секций учитывается один раз за запуск."""
    configs = (config for _, config in vendors if config is not None)
    routings = {config.routing for config in configs if config.routing is not None}
    return sum(routing.unrouted_rows for routing in routings)
