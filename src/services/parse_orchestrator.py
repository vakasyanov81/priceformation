"""Оркестрация парсинга прайс-листов поставщиков и группировки.

Сервис заменяет бывший ``CommonPrice``: разбирает прайсы всех (или одного)
поставщиков, собирает статистику пропусков и группирует результат.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Protocol, cast

from core import err_msg, log_msg, warn_msg
from parsers.all_vendors import all_vendors, vendor_config_is_enabled
from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.base_parser_config import ParseConfiguration
from parsers.base_parser.category_finder import skipped_unknown_categories_message
from parsers.base_parser.markup_policy import MarkupPolicy
from parsers.common_price_grouper import CommonPriceGrouper
from parsers.data_provider.black_list import skipped_black_list_message
from parsers.data_provider.manufacturer_aliases import clear_manufacturer_aliases_cache
from parsers.data_provider.vendor_list import VendorListConfigFileError
from parsers.registry import vendor_entry_for, vendor_markup_policy_for
from parsers.row_item.row_item import RowItem
from services.service_provider import ServiceProvider

type VendorList = Sequence[tuple[type[BaseParser], ParseConfiguration | None]]
type UnknownCategorySkip = tuple[str, str]


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


@dataclass
class ParseResult:
    """Результат разбора и группировки: записи и накопленные пропуски."""

    parsed_items: list[RowItem] = field(default_factory=list)
    unknown_category_skips: list[UnknownCategorySkip] = field(default_factory=list)
    black_list_skips: int = 0


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
        start_time = time.monotonic()
        log_msg('\n============== Начало разбора прайсов =================\n', need_print_log=True)
        self._parse_all_vendors(parse_result, vendors)
        self._log_skips(parse_result)
        clear_manufacturer_aliases_cache()
        grouper = self._grouper_factory(parse_result.parsed_items)
        parse_result.parsed_items = grouper.group_by_params().get_row_items()
        log_msg(f'\nКоличество дублей: {len(grouper.get_double_row_items())}\n', need_print_log=True)
        elapsed = time.monotonic() - start_time
        log_msg(f'\n===== Окончание разбора прайсов ({elapsed:.2f} сек) ========\n', need_print_log=True)
        return parse_result

    def _parse_all_vendors(self, parse_result: ParseResult, vendors: VendorList) -> None:
        """Проход по списку поставщиков: разбор каждого через фабрику парсеров."""
        for vendor_cls, vendor_config in vendors:
            self._parse_supplier(parse_result, _parser_for_vendor(self._parser_factory, vendor_cls, vendor_config))

    def _parse_supplier(self, parse_result: ParseResult, parser: BaseParser) -> None:
        """Парсит прайс одного поставщика и добавляет записи к результату."""
        try:
            parsed = parser.parse()
        except VendorListConfigFileError:
            warn_msg('Отсутствует файл конфигурации parse_config/vendor_list.json', need_print_log=True)
        except Exception as exc:
            err_msg(f'Ошибка разбора прайса поставщика {parser!r} // {exc}')
            raise
        else:
            parse_result.parsed_items.extend(parsed)
            parse_result.unknown_category_skips.extend(_parser_unknown_skips(parser))
            parse_result.black_list_skips += _black_list_skip_count(parser)

    def _log_skips(self, parse_result: ParseResult) -> None:
        """Печать сводки по пропускам категорий и black_list."""
        category_message = skipped_unknown_categories_message(parse_result.unknown_category_skips)
        if category_message:
            warn_msg(category_message, need_print_log=True)
        black_list_message = skipped_black_list_message(parse_result.black_list_skips)
        if black_list_message:
            log_msg(black_list_message, need_print_log=True)


def _parser_for_vendor(
    parser_factory: ParserFactory,
    vendor_cls: type[BaseParser],
    vendor_config: ParseConfiguration | None,
) -> BaseParser:
    """Собрать парсер поставщика с учётом активности и политики наценки."""
    if vendor_config is None:
        return vendor_cls(vendor_config)
    if not vendor_config_is_enabled(vendor_config):
        return vendor_cls(parse_config=vendor_config)
    return parser_factory(
        vendor_cls,
        vendor_config,
        markup_policy=vendor_markup_policy_for(vendor_cls, vendor_config),
    )


def _parser_unknown_skips(parser: BaseParser) -> list[UnknownCategorySkip]:
    """Пропуски неизвестных категорий парсера с именем поставщика."""
    skips = getattr(parser, 'unknown_category_skips', ())
    if not isinstance(skips, list) or not skips:
        return []
    supplier = parser.parser_params().supplier.name
    return [(supplier, category) for category in skips]


def _black_list_skip_count(parser: BaseParser) -> int:
    """Сколько записей парсер отбросил по black_list; игнорируем не-int заглушки."""
    count = getattr(parser, 'black_list_skips', 0)
    return count if isinstance(count, int) else 0
