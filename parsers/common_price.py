# -*- coding: utf-8 -*-
"""
Make parse all price and make inner an drom prices
"""
__author__ = "Kasyanov V.A."

from typing import Dict, List, NamedTuple, Optional, Tuple, Type

from parsers import data_provider
from parsers.all_vendors import all_vendors
from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.base_parser_config import (
    BasePriceParseConfiguration,
    BasePriceParseConfigurationParams,
)
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
        self.parse_vendors(all_vendors())

    def parse_vendors(
        self,
        vendors: List[
            Tuple[Type[BaseParser], Optional[Type[BasePriceParseConfiguration]]]
        ],
    ):
        """
        make parse prices by vendor-list
        :return:
        """
        for vendor in vendors:
            self.result += self.instance_vendor(vendor).get_result()

    @classmethod
    def instance_vendor(
        cls,
        vendor: Tuple[Type[BaseParser], Optional[Type[BasePriceParseConfiguration]]],
    ):
        """instance vendor"""
        mark_up_provider = data_provider.MarkupRulesProviderFromUserConfig(
            vendor[0].__SUPPLIER_FOLDER_NAME__
        )
        default_config = BasePriceParseConfigurationParams(
            markup_rules_provider=mark_up_provider,
            black_list_provider=data_provider.BlackListProviderFromUserConfig(),
            stop_words_provider=data_provider.StopWordsProviderFromUserConfig(),
            vendor_list=data_provider.VendorListProviderFromUserConfig(),
            manufacturer_aliases=data_provider.ManufacturerAliasesProviderFromUserConfig(),
        )
        config = vendor[1](default_config) if vendor[1] else None
        return vendor[0](price_config=config)

    @classmethod
    def supplier_info(cls) -> Dict[str, SupplierInfo]:
        """Supplier info"""
        supplier_info = {}
        for v, _ in all_vendors():
            supplier_info[v.__SUPPLIER_CODE__] = SupplierInfo(name=v.__SUPPLIER_NAME__)
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
