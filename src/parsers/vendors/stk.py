# -*- coding: utf-8 -*-
"""
# stk
"""
__author__ = "Kasyanov V.A."

from src.parsers import data_provider
from src.parsers.base_parser.base_parser import BaseParser, ParserParams
from src.parsers.base_parser.base_parser_config import (
    BasePriceParseConfigurationParams,
    ParseConfiguration,
    ParseParamsSupplier,
)
from src.parsers.row_item.row_item import RowItem

stk_params = ParserParams(
    supplier=ParseParamsSupplier(folder_name="stk", name="STK", code="7"),
    start_row=14,
    sheet_info="",
    columns={
        1: RowItem.__CODE__,
        2: RowItem.__TITLE__,
        3: RowItem.__PRICE_PURCHASE__,
        4: RowItem.__REST_COUNT__,
    },
    stop_words=[],
    file_templates=["price*.xls", "price*.xlsx"],
    sheet_indexes=[],
    row_item_adaptor=RowItem,
)


mark_up_provider = data_provider.MarkupRulesProviderFromUserConfig(stk_params.supplier.folder_name)

stk_config = BasePriceParseConfigurationParams(
    markup_rules_provider=mark_up_provider,
    black_list_provider=data_provider.BlackListProviderFromUserConfig(),
    stop_words_provider=data_provider.StopWordsProviderFromUserConfig(),
    vendor_list=data_provider.VendorListProviderFromUserConfig(),
    manufacturer_aliases=data_provider.ManufacturerAliasesProviderFromUserConfig(),
    parser_params=stk_params,
)

stk_config = ParseConfiguration(stk_config)


class STKParser(BaseParser):
    """
    parser for Greenstone vendor
    """

    def process(self):
        res = super().process()
        for item in self.result:
            self.skip_by_min_rest(item)
            self.add_price_markup(item)

        return res

    def add_price_markup(self, item):
        """
        Добавить наценку
        """

        if not item.price_opt:
            return
        item.price_markup = self.round_price(item.price_opt * 1.06)
