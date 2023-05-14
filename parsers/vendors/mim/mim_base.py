# -*- coding: utf-8 -*-
"""
base logic for mim vendor
"""
__author__ = "Kasyanov V.A."

from parsers import data_provider
from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.base_parser_config import (
    BasePriceParseConfigurationParams,
    ParseConfiguration,
    ParserParams,
)
from parsers.row_item.vendors.row_item_mim import RowItemMim

mim_params = ParserParams(
    supplier_folder_name="mim",
    start_row=2,
    supplier_name="Мим",
    supplier_code="4",
    sheet_info="",
    columns={},
    stop_words=[],
    file_templates=["price*.xls", "price*.xlsx"],
    sheet_indexes=[],
    row_item_adaptor=RowItemMim,
)


mark_up_provider = data_provider.MarkupRulesProviderFromUserConfig(
    mim_params.supplier_folder_name
)

mim_config = BasePriceParseConfigurationParams(
    markup_rules_provider=mark_up_provider,
    black_list_provider=data_provider.BlackListProviderFromUserConfig(),
    stop_words_provider=data_provider.StopWordsProviderFromUserConfig(),
    vendor_list=data_provider.VendorListProviderFromUserConfig(),
    manufacturer_aliases=data_provider.ManufacturerAliasesProviderFromUserConfig(),
    parser_params=mim_params,
)

mim_config = ParseConfiguration(mim_config)


class MimParserBase(BaseParser):
    """
    base logic for mim vendor
    """

    @classmethod
    def get_current_category(cls):
        """getting current category"""
        raise NotImplementedError()

    @classmethod
    def set_category(cls, item):
        """set category to row price item"""
        item.type_production = cls.get_current_category()

    def process(self):
        """parse process"""
        res = super().process()
        for item in self.result:
            self.add_price_markup(item)
            self.skip_by_min_rest(item)
            self.set_category(item)
            self.correction_category(item)
        return res
