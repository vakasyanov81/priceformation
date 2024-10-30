# -*- coding: utf-8 -*-
"""
Make parse all price and make inner an drom prices
"""
__author__ = "Kasyanov V.A."

from typing import Dict, List, NamedTuple, Optional, Tuple, Type

from core import warn_msg
from parsers.all_vendors import all_vendors
from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.base_parser_config import ParseConfiguration
from parsers.data_provider.vendor_list import VendorListConfigFileError
from parsers.writer.templates.all_templates import all_writer_templates
from parsers.writer.xls_writer import XlsWriter
from parsers.writer.xwlt_driver import XlsxWriterDriver


class SupplierInfo(NamedTuple):
    name: str


class CommonPrice:
    """
    Make parse all price and make inner an drom prices
    """

    def __init__(self, xls_writer=XlsWriter, write_driver=XlsxWriterDriver):
        """init"""
        self.xls_writer = xls_writer
        self.write_driver = write_driver
        self.result = []

    def parse_all_vendors(self):
        """
        make parse all prices
        :return:
        """
        try:
            self.parse_vendors(all_vendors())
        except VendorListConfigFileError:
            warn_msg("Отсутствует файл конфигурации parse_config/vendor_list.json", need_print_log=True)

    def parse_vendors(
        self,
        vendors: List[Tuple[Type[BaseParser], Optional[Type[ParseConfiguration]]]],
    ):
        """
        make parse prices by vendor-list
        :return:
        """
        for vendor, vendor_config in vendors:
            self.result += self.instance_vendor(vendor, vendor_config).parse()

    @classmethod
    def instance_vendor(cls, vendor: Type[BaseParser], config: Type[ParseConfiguration] | None):
        """instance vendor"""
        return vendor(config)

    @classmethod
    def supplier_info(cls) -> Dict[str, SupplierInfo]:
        """Supplier info"""
        supplier_info = {}
        for _, config in all_vendors():
            supplier_info[config.parse_config.parser_params.supplier.code] = SupplierInfo(
                name=config.parse_config.parser_params.supplier.name
            )
        return supplier_info

    def write_all_prices(self):
        """
        Make prices for all active templates
        :return:
        """
        # TODO add test

        for write_template in all_writer_templates():
            self.xls_writer(
                self.write_driver(),
                BaseParser.to_raw_result(self.result),
                write_template,
            )
