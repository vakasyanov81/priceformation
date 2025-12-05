"""
Make parse all price and make inner and drom prices
"""

import time
from typing import TypeVar

from core import warn_msg, err_msg, log_msg
from parsers.all_vendors import all_vendor_supplier_info
from parsers.base_parser.base_parser import Parser
from parsers.base_parser.base_parser_config import ParseConfiguration
from parsers.common_price_grouper import CommonPriceGrouper
from parsers.data_provider.vendor_list import VendorListConfigFileError
from parsers.writer.xls_writer import XlsWriter
from parsers.writer.xwlt_driver import XlsxWriterDriver

SupplierName = str
SupplierCode = str

VendorList = TypeVar("VendorList", bound=list[tuple[type[Parser], type[ParseConfiguration] | None]])


class CommonPrice:
    """
    Make parse all price and make inner and drom prices
    """

    def __init__(self, xls_writer=XlsWriter, write_driver=XlsxWriterDriver):
        """init"""
        self.xls_writer = xls_writer
        self.write_driver = write_driver
        self._result = []

    def parse_all_vendors(self, vendors: VendorList):
        """
        make parse all prices
        :return:
        """
        start_time = time.time()
        log_msg("\n============== Начало разбора прайсов =================\n", need_print_log=True)
        for vendor, vendor_config in vendors:
            self.parse_vendor(vendor(vendor_config))
        grouper = CommonPriceGrouper(self.get_result())
        self._result = grouper.group_by_params().get_items()
        log_msg(f"\nКоличество дублей: {grouper.get_double_count()}\n", need_print_log=True)
        elapsed_time = time.time() - start_time

        log_msg(
            f"\n===== Окончание разбора прайсов ({elapsed_time:.2f} секунд) ========\n",
            need_print_log=True,
        )

    def parse_vendor(self, parser):
        try:
            self._result += parser.parse()
        except VendorListConfigFileError:
            warn_msg(
                "Отсутствует файл конфигурации parse_config/vendor_list.json",
                need_print_log=True,
            )
        except Exception as exc:
            err_msg(f"Ошибка разбора прайса поставщика {repr(parser)} // {str(exc)}")
            raise exc

    @classmethod
    def supplier_info(cls) -> dict[SupplierCode, SupplierName]:
        """Supplier info"""
        return all_vendor_supplier_info()

    def get_result(self):
        """get result"""
        return self._result
