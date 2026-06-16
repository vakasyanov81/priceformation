"""
Парсинг прайс-листов всех поставщиков и формирование внутренних цен.
"""

import time
from typing import TypeAlias

from core import warn_msg, err_msg, log_msg
from parsers.all_vendors import all_vendor_supplier_info
from parsers.base_parser.base_parser import Parser
from parsers.base_parser.base_parser_config import ParseConfiguration
from parsers.common_price_grouper import CommonPriceGrouper
from parsers.data_provider.vendor_list import VendorListConfigFileError
from parsers.writer.xls_writer import XlsWriter
from parsers.writer.xwlt_driver import XlsxWriterDriver

SupplierName: TypeAlias = str
SupplierCode: TypeAlias = str

VendorList: TypeAlias = list[tuple[type[Parser], type[ParseConfiguration] | None]]


class CommonPrice:
    """
    Агрегирует результаты парсинга прайс-листов всех поставщиков,
    выполняет группировку и дедупликацию, предоставляет итоговый результат.
    """

    def __init__(
        self,
        xls_writer: type[XlsWriter] = XlsWriter,
        write_driver: type[XlsxWriterDriver] = XlsxWriterDriver,
    ) -> None:
        self.xls_writer = xls_writer
        self.write_driver = write_driver
        self._result: list = []

    def parse_all_vendors(self, vendors: VendorList) -> None:
        """Запускает парсинг по всем поставщикам и группирует результат."""
        self._result.clear()  # защищаемся от накопления при повторных вызовах

        start_time = time.monotonic()
        log_msg("\n============== Начало разбора прайсов =================\n", need_print_log=True)

        for vendor_cls, vendor_config in vendors:
            self.parse_vendor(vendor_cls(vendor_config))

        grouper = CommonPriceGrouper(self._result)
        self._result = grouper.group_by_params().get_items()

        log_msg(f"\nКоличество дублей: {grouper.get_double_count()}\n", need_print_log=True)

        elapsed = time.monotonic() - start_time
        log_msg(f"\n===== Окончание разбора прайсов ({elapsed:.2f} сек) ========\n", need_print_log=True)

    def parse_vendor(self, parser: Parser) -> None:
        """Парсит прайс одного поставщика и добавляет записи к общему результату."""
        try:
            self._result.extend(parser.parse())

        except VendorListConfigFileError:
            warn_msg(
                "Отсутствует файл конфигурации parse_config/vendor_list.json",
                need_print_log=True,
            )

        except Exception as exc:
            err_msg(f"Ошибка разбора прайса поставщика {parser!r} // {exc}")
            raise

    @property
    def result(self) -> list:
        """Итоговый список записей."""
        return self._result

    @staticmethod
    def supplier_info() -> dict[SupplierCode, SupplierName]:
        """Возвращает отображение код поставщика → название."""
        return all_vendor_supplier_info()
