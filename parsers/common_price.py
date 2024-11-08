# -*- coding: utf-8 -*-
"""
Make parse all price and make inner and drom prices
"""
__author__ = "Kasyanov V.A."

from typing import TypeVar

from core import warn_msg
from parsers.all_vendors import all_vendors, all_vendor_supplier_info
from parsers.base_parser.base_parser import BaseParser, Parser
from parsers.base_parser.base_parser_config import ParseConfiguration
from parsers.data_provider.vendor_list import VendorListConfigFileError
from parsers.writer.templates.all_templates import all_writer_templates
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
        try:
            for vendor, vendor_config in vendors:
                self._result += vendor(vendor_config).parse()
        except VendorListConfigFileError:
            warn_msg("Отсутствует файл конфигурации parse_config/vendor_list.json", need_print_log=True)

    @classmethod
    def supplier_info(cls) -> dict[SupplierCode, SupplierName]:
        """Supplier info"""
        return all_vendor_supplier_info()

    def get_result(self):
        """get result"""
        return self._result

    def write_all_prices(self):
        """
        Make prices for all active templates
        :return:
        """
        # TODO add test

        for write_template in all_writer_templates():
            self.xls_writer(
                self.write_driver(),
                BaseParser.to_raw_result(self._result),
                write_template,
            )
