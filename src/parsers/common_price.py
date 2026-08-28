"""
Парсинг прайс-листов всех поставщиков и формирование внутренних цен.
"""

import time
from collections.abc import Sequence

from core import err_msg, log_msg, warn_msg
from parsers.all_vendors import all_vendor_supplier_info
from parsers.base_parser.base_parser import BaseParser, make_parser
from parsers.base_parser.base_parser_config import ParseConfiguration
from parsers.base_parser.category_finder import skipped_unknown_categories_message
from parsers.base_parser.markup_policy import (
    IdentityMarkupPolicy,
    MarkupPolicy,
    RecommendedOrMapMarkupPolicy,
    make_map_on_opt_markup_policy,
)
from parsers.common_price_grouper import CommonPriceGrouper
from parsers.data_provider.black_list import skipped_black_list_message
from parsers.data_provider.manufacturer_aliases import clear_manufacturer_aliases_cache
from parsers.data_provider.vendor_list import VendorListConfigFileError
from parsers.row_item.row_item import RowItem
from parsers.vendors.autosnab54_ru import Autosnab54Parser
from parsers.vendors.four_tochki.four_tochki_sheet1 import FourTochkiParser1Sheet
from parsers.vendors.pioner import PionerParser
from parsers.vendors.poshk import PoshkParser
from parsers.vendors.stk import STKParser

type SupplierName = str
type SupplierCode = str

type VendorList = Sequence[tuple[type[BaseParser], ParseConfiguration | None]]
type UnknownCategorySkip = tuple[str, str]


class CommonPrice:
    """
    Агрегирует результаты парсинга прайс-листов всех поставщиков,
    выполняет группировку и дедупликацию, предоставляет итоговый результат.
    """

    def __init__(self) -> None:
        self._parsed_items: list[RowItem] = []
        self._unknown_category_skips: list[UnknownCategorySkip] = []
        self._black_list_skips = 0

    def parse_all_vendors(self, vendors: VendorList) -> None:
        """Запускает парсинг по всем поставщикам и группирует результат."""
        self._parsed_items.clear()  # защищаемся от накопления при повторных вызовах
        self._unknown_category_skips.clear()
        self._black_list_skips = 0

        start_time = time.monotonic()
        log_msg("\n============== Начало разбора прайсов =================\n", need_print_log=True)

        for vendor_cls, vendor_config in vendors:
            self.parse_vendor(_parser_for_vendor(vendor_cls, vendor_config))

        self._log_unknown_category_skips()
        grouper = _price_run_grouper(self._parsed_items)
        self._parsed_items = grouper.group_by_params().get_row_items()

        log_msg(f"\nКоличество дублей: {len(grouper.get_double_row_items())}\n", need_print_log=True)

        elapsed = time.monotonic() - start_time
        log_msg(f"\n===== Окончание разбора прайсов ({elapsed:.2f} сек) ========\n", need_print_log=True)

    def parse_vendor(self, parser: BaseParser) -> None:
        """Парсит прайс одного поставщика и добавляет записи к общему результату."""
        try:
            parsed = parser.parse()
        except VendorListConfigFileError:
            warn_msg("Отсутствует файл конфигурации parse_config/vendor_list.json", need_print_log=True)
        except Exception as exc:
            err_msg(f"Ошибка разбора прайса поставщика {parser!r} // {exc}")
            raise
        else:
            self._parsed_items.extend(parsed)
            self._remember_unknown_category_skips(parser)
            self._black_list_skips += _black_list_skip_count(parser)

    def _remember_unknown_category_skips(self, parser: BaseParser) -> None:
        skips = getattr(parser, "unknown_category_skips", ())
        if not isinstance(skips, list) or not skips:
            return
        supplier = parser.parser_params().supplier.name
        self._unknown_category_skips.extend((supplier, category) for category in skips)

    def _log_unknown_category_skips(self) -> None:
        message = skipped_unknown_categories_message(self._unknown_category_skips)
        if message:
            warn_msg(message, need_print_log=True)
        black_list_message = skipped_black_list_message(self._black_list_skips)
        if black_list_message:
            log_msg(black_list_message, need_print_log=True)

    @property
    def parsed_items(self) -> list[RowItem]:
        """Итоговый список записей."""
        return self._parsed_items

    def supplier_info(self) -> dict[SupplierCode, SupplierName]:
        """Возвращает отображение код поставщика → название."""
        return all_vendor_supplier_info()


_MAP_ON_OPT_VENDORS: tuple[type[BaseParser], ...] = (PoshkParser, PionerParser, STKParser)
_IDENTITY_VENDORS: tuple[type[BaseParser], ...] = (Autosnab54Parser,)
_RECOMMENDED_OR_MAP_VENDORS: tuple[type[BaseParser], ...] = (FourTochkiParser1Sheet,)


def _black_list_skip_count(parser: BaseParser) -> int:
    """Rows a vendor parser dropped by black_list; ignore non-int stubs."""
    count = getattr(parser, "black_list_skips", 0)
    if isinstance(count, int):
        return count
    return 0


def _price_run_grouper(row_items: list[RowItem]) -> CommonPriceGrouper:
    """Сброс aliases-кэша на прогон, затем группировка со свежей картой."""
    clear_manufacturer_aliases_cache()
    return CommonPriceGrouper(row_items)


def _vendor_is_enabled(vendor_config: ParseConfiguration) -> bool:
    folder_name = vendor_config.supplier.folder_name
    vendor = vendor_config.all_vendor_config().get(folder_name)
    return bool(vendor and vendor.enabled)


def _markup_policy_for_vendor(
    vendor_cls: type[BaseParser],
    vendor_config: ParseConfiguration,
) -> MarkupPolicy | None:
    if vendor_cls in _MAP_ON_OPT_VENDORS:
        return make_map_on_opt_markup_policy(vendor_config)
    if vendor_cls in _IDENTITY_VENDORS:
        return IdentityMarkupPolicy.create()
    if vendor_cls in _RECOMMENDED_OR_MAP_VENDORS:
        return RecommendedOrMapMarkupPolicy.from_config(vendor_config)
    return None


def _parser_for_vendor(
    vendor_cls: type[BaseParser],
    vendor_config: ParseConfiguration | None,
) -> BaseParser:
    if vendor_config is None:
        return vendor_cls(vendor_config)
    try:
        enabled = _vendor_is_enabled(vendor_config)
    except VendorListConfigFileError:
        enabled = False
    if not enabled:
        return vendor_cls(parse_config=vendor_config)
    return make_parser(
        vendor_cls,
        vendor_config,
        markup_policy=_markup_policy_for_vendor(vendor_cls, vendor_config),
    )
