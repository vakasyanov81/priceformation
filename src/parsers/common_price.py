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
from parsers.base_parser.markup_policy import make_map_on_opt_markup_policy
from parsers.common_price_grouper import CommonPriceGrouper
from parsers.data_provider.vendor_list import VendorListConfigFileError
from parsers.row_item.row_item import RowItem
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

    def parse_all_vendors(self, vendors: VendorList) -> None:
        """Запускает парсинг по всем поставщикам и группирует результат."""
        self._parsed_items.clear()  # защищаемся от накопления при повторных вызовах
        self._unknown_category_skips.clear()

        start_time = time.monotonic()
        log_msg("\n============== Начало разбора прайсов =================\n", need_print_log=True)

        for vendor_cls, vendor_config in vendors:
            self.parse_vendor(_parser_for_vendor(vendor_cls, vendor_config))

        self._log_unknown_category_skips()
        grouper = CommonPriceGrouper(self._parsed_items)
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

    @property
    def parsed_items(self) -> list[RowItem]:
        """Итоговый список записей."""
        return self._parsed_items

    def supplier_info(self) -> dict[SupplierCode, SupplierName]:
        """Возвращает отображение код поставщика → название."""
        return all_vendor_supplier_info()


_MAP_ON_OPT_VENDORS: tuple[type[BaseParser], ...] = (PoshkParser, PionerParser, STKParser)


def _parser_for_vendor(
    vendor_cls: type[BaseParser],
    vendor_config: ParseConfiguration | None,
) -> BaseParser:
    if vendor_config is None:
        return vendor_cls(vendor_config)
    markup_policy = make_map_on_opt_markup_policy(vendor_config) if vendor_cls in _MAP_ON_OPT_VENDORS else None
    return make_parser(vendor_cls, vendor_config, markup_policy=markup_policy)
