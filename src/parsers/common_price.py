"""
Парсинг прайс-листов всех поставщиков и формирование внутренних цен.
"""

import time
from collections.abc import Sequence
from typing import Protocol, cast

from core import err_msg, log_msg, warn_msg
from parsers.all_vendors import vendor_config_is_enabled
from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.base_parser_config import ParseConfiguration
from parsers.base_parser.category_finder import skipped_unknown_categories_message
from parsers.base_parser.markup_policy import MarkupPolicy
from parsers.common_price_grouper import CommonPriceGrouper
from parsers.data_provider.black_list import skipped_black_list_message
from parsers.data_provider.manufacturer_aliases import clear_manufacturer_aliases_cache
from parsers.data_provider.vendor_list import VendorListConfigFileError
from parsers.registry import vendor_markup_policy_for
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


class CommonPrice:
    """
    Агрегирует результаты парсинга прайс-листов всех поставщиков,
    выполняет группировку и дедупликацию, предоставляет итоговый результат.
    """

    def __init__(self, grouper_factory: GrouperFactory | None = None) -> None:
        self._grouper_factory = grouper_factory or cast(GrouperFactory, ServiceProvider.resolve(GrouperFactory))
        self._parsed_items: list[RowItem] = []
        self.unknown_category_skips: list[UnknownCategorySkip] = []
        self.black_list_skips = 0

    def parse_all_vendors(self, vendors: VendorList) -> None:
        """Запускает парсинг по всем поставщикам и группирует результат."""
        self._parsed_items.clear()  # защищаемся от накопления при повторных вызовах
        self.unknown_category_skips.clear()
        self.black_list_skips = 0

        start_time = time.monotonic()
        log_msg('\n============== Начало разбора прайсов =================\n', need_print_log=True)

        for vendor_cls, vendor_config in vendors:
            self.parse_vendor(_parser_for_vendor(vendor_cls, vendor_config))

        self._log_unknown_category_skips()
        grouper = _price_run_grouper(self._parsed_items, self._grouper_factory)
        self._parsed_items = grouper.group_by_params().get_row_items()

        log_msg(f'\nКоличество дублей: {len(grouper.get_double_row_items())}\n', need_print_log=True)

        elapsed = time.monotonic() - start_time
        log_msg(f'\n===== Окончание разбора прайсов ({elapsed:.2f} сек) ========\n', need_print_log=True)

    def parse_vendor(self, parser: BaseParser) -> None:
        """Парсит прайс одного поставщика и добавляет записи к общему результату."""
        try:
            parsed = parser.parse()
        except VendorListConfigFileError:
            warn_msg('Отсутствует файл конфигурации parse_config/vendor_list.json', need_print_log=True)
        except Exception as exc:
            err_msg(f'Ошибка разбора прайса поставщика {parser!r} // {exc}')
            raise
        else:
            self._parsed_items.extend(parsed)
            self._remember_unknown_category_skips(parser)
            self.black_list_skips += _black_list_skip_count(parser)

    def _remember_unknown_category_skips(self, parser: BaseParser) -> None:
        skips = getattr(parser, 'unknown_category_skips', ())
        if not isinstance(skips, list) or not skips:
            return
        supplier = parser.parser_params().supplier.name
        self.unknown_category_skips.extend((supplier, category) for category in skips)

    def _log_unknown_category_skips(self) -> None:
        message = skipped_unknown_categories_message(self.unknown_category_skips)
        if message:
            warn_msg(message, need_print_log=True)
        black_list_message = skipped_black_list_message(self.black_list_skips)
        if black_list_message:
            log_msg(black_list_message, need_print_log=True)

    @property
    def parsed_items(self) -> list[RowItem]:
        """Итоговый список записей."""
        return self._parsed_items


def _black_list_skip_count(parser: BaseParser) -> int:
    """Rows a vendor parser dropped by black_list; ignore non-int stubs."""
    count = getattr(parser, 'black_list_skips', 0)
    if isinstance(count, int):
        return count
    return 0


def _price_run_grouper(row_items: list[RowItem], grouper_factory: GrouperFactory) -> CommonPriceGrouper:
    """Сброс aliases-кэша на прогон, затем группировка со свежей картой."""
    clear_manufacturer_aliases_cache()
    return grouper_factory(row_items)


def _parser_for_vendor(
    vendor_cls: type[BaseParser],
    vendor_config: ParseConfiguration | None,
) -> BaseParser:
    if vendor_config is None:
        return vendor_cls(vendor_config)
    if not vendor_config_is_enabled(vendor_config):
        return vendor_cls(parse_config=vendor_config)
    parser_factory = cast(ParserFactory, ServiceProvider.resolve(ParserFactory))
    return parser_factory(
        vendor_cls,
        vendor_config,
        markup_policy=vendor_markup_policy_for(vendor_cls, vendor_config),
    )
