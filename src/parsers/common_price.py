# -*- coding: utf-8 -*-
"""
Make parse all price and make inner and drom prices
"""
__author__ = "Kasyanov V.A."

import time
from typing import TypeVar

from src.core import warn_msg, err_msg, log_msg
from src.parsers.all_vendors import all_vendor_supplier_info
from src.parsers.base_parser.base_parser import BaseParser, Parser
from src.parsers.base_parser.base_parser_config import ParseConfiguration
from src.parsers.base_parser.nomenclature_correction import get_nomenclature_corrected_title
from src.parsers.data_provider.vendor_list import VendorListConfigFileError
from src.parsers.writer.templates.all_templates import all_writer_templates
from src.parsers.writer.xls_writer import XlsWriter
from src.parsers.writer.xwlt_driver import XlsxWriterDriverV2

SupplierName = str
SupplierCode = str

VendorList = TypeVar("VendorList", bound=list[tuple[type[Parser], type[ParseConfiguration] | None]])


class CommonPrice:
    """
    Make parse all price and make inner and drom prices
    """

    def __init__(self, xls_writer=XlsWriter, write_driver=XlsxWriterDriverV2):
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
            _parser = vendor(vendor_config)
            try:
                self._result += _parser.parse()
            except VendorListConfigFileError:
                warn_msg(
                    "Отсутствует файл конфигурации parse_config/vendor_list.json",
                    need_print_log=True,
                )
            except Exception as exc:
                err_msg(f"Ошибка разбора прайса поставщика {repr(_parser)} // {str(exc)}")
                raise exc
        elapsed_time = time.time() - start_time
        log_msg(
            f"\n===== Окончание разбора прайсов ({elapsed_time:.2f} секунд) ========\n",
            need_print_log=True,
        )

    @classmethod
    def supplier_info(cls) -> dict[SupplierCode, SupplierName]:
        """Supplier info"""
        return all_vendor_supplier_info()

    def get_result(self):
        """get result"""
        return self._result

    def nomenclature_title_correction(self):
        for item in self._result:
            item.title = get_nomenclature_corrected_title(item.title)

    def write_all_prices(self):
        """
        Make prices for all active templates
        :return:
        """
        # TODO add test
        self.nomenclature_title_correction()
        for write_template in all_writer_templates():
            self.xls_writer(
                self.write_driver(),
                BaseParser.to_raw_result(self._result),
                write_template,
            )
