"""Оркестрация парсинга прайс-листов поставщиков и группировки.

Сервис заменяет бывший ``CommonPrice``: разбирает прайсы всех (или одного)
поставщиков, собирает статистику пропусков и группирует результат.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable, Sequence
from typing import Protocol, cast

from domain.row_item.row_item import RowItem
from infrastructure.logging.file_logging import clear_log_files
from parsers.all_vendors import all_vendors
from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.base_parser_config import ParseConfiguration
from parsers.base_parser.markup_policy import MarkupPolicy
from parsers.common_price.grouper import CommonPriceGrouper
from parsers.data_provider.manufacturer_aliases import clear_manufacturer_aliases_cache
from parsers.registry import vendor_entry_for
from services.parse_logging import LogMessage, log_parse_failure, parser_messages, skips_messages
from services.parse_result import ParseResult, UnknownCategorySkip
from services.service_provider import ServiceProvider
from services.vendor_parser import parser_for_vendor

logger = logging.getLogger(__name__)

type VendorList = Sequence[tuple[type[BaseParser], ParseConfiguration | None]]


class ParserFactory(Protocol):
    """Фабрика вендорного парсера: класс и конфиг → экземпляр."""

    def __call__(
        self,
        parser_cls: type[BaseParser],
        parse_config: ParseConfiguration,
        *,
        markup_policy: MarkupPolicy | None = None,
    ) -> BaseParser:
        """Собрать парсер поставщика."""
        ...


class GrouperFactory(Protocol):
    """Фабрика группировщика: записи прайса → CommonPriceGrouper."""

    def __call__(self, row_items: list[RowItem]) -> CommonPriceGrouper:
        """Создать группировщик для списка записей."""
        ...


class ParseOrchestrator:
    """Парсит прайс-листы поставщиков и группирует результат."""

    def __init__(
        self,
        *,
        grouper_factory: GrouperFactory | None = None,
        parser_factory: ParserFactory | None = None,
        vendors_provider: Callable[[], VendorList] | None = None,
    ) -> None:
        self._grouper_factory = grouper_factory or cast(GrouperFactory, ServiceProvider.resolve(GrouperFactory))
        self._parser_factory = parser_factory or cast(ParserFactory, ServiceProvider.resolve(ParserFactory))
        self._vendors_provider = vendors_provider or all_vendors

    def parse_all(self, vendors: VendorList | None = None) -> ParseResult:
        """Парсит всех поставщиков (или переданный список) и группирует."""
        return self._parse_vendors(self._vendors_provider() if vendors is None else vendors)

    def parse_vendor(self, code: str) -> ParseResult:
        """Парсит одного поставщика по коду реестра и группирует."""
        return self._parse_vendors([vendor_entry_for(code)])

    def _parse_vendors(self, vendors: VendorList) -> ParseResult:
        """Общий цикл разбора списка поставщиков с итоговой группировкой."""
        parse_result = ParseResult()
        clear_log_files()
        start_time = time.monotonic()
        logger.info('\n============== Начало разбора прайсов =================\n')
        self._parse_all_vendors(parse_result, vendors)
        _emit(skips_messages(parse_result))
        clear_manufacturer_aliases_cache()
        grouper = self._grouper_factory(parse_result.parsed_items)
        parse_result.parsed_items = grouper.group_by_params().get_row_items()
        logger.info(f'\nКоличество дублей: {len(grouper.get_double_row_items())}\n')
        elapsed = time.monotonic() - start_time
        logger.info(f'\n===== Окончание разбора прайсов ({elapsed:.2f} сек) ========\n')
        return parse_result

    def _parse_all_vendors(self, parse_result: ParseResult, vendors: VendorList) -> None:
        """Проход по списку поставщиков: разбор каждого через фабрику парсеров."""
        for vendor_cls, vendor_config in vendors:
            self._parse_supplier(parse_result, parser_for_vendor(vendor_cls, vendor_config))

    def _parse_supplier(self, parse_result: ParseResult, parser: BaseParser) -> None:
        """Парсит прайс одного поставщика и добавляет записи к результату."""
        try:
            parsed = parser.parse()
        except Exception as exc:
            log_parse_failure(logger, parser, exc)
            raise
        else:
            parse_result.parsed_items.extend(parsed)
            parse_result.unknown_category_skips.extend(_parser_unknown_skips(parser))
            parse_result.black_list_skips += parser.stats.black_list_skips
            parse_result.type_corrections += parser.stats.type_corrections
            parse_result.title_conflicts += parser.stats.title_conflicts
            parse_result.titles_not_composed += parser.stats.titles_not_composed
            parse_result.homoglyph_fixes += parser.stats.homoglyph_fixes
            parse_result.homoglyph_suspects += parser.stats.homoglyph_suspects
            _emit(parser_messages(parser))


def _emit(messages: list[LogMessage]) -> None:
    """Записать сообщения сводки в лог оркестратора."""
    for level, text in messages:
        logger.log(level, text)


def _parser_unknown_skips(parser: BaseParser) -> list[UnknownCategorySkip]:
    """Пропуски неизвестных категорий парсера с именем поставщика."""
    skips = parser.stats.unknown_category_skips
    if not skips:
        return []
    supplier = parser.settings.parser_params().supplier.name
    return [(supplier, category) for category in skips]
