# -*- coding: utf-8 -*-
"""
logic for autosnab54_ru vendor
"""
__author__ = "Kasyanov V.A."

from parsers import data_provider
from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.base_parser_config import (
    BasePriceParseConfigurationParams,
    ParseConfiguration,
    ParserParams, ParseParamsSupplier,
)
from parsers.row_item.row_item import RowItem

autosnab_params = ParserParams(
    supplier=ParseParamsSupplier(
        folder_name='autosnab54_ru',
        name='Автоснабжение',
        code='6'
    ),
    start_row=2,
    sheet_info="",
    columns={
        0: RowItem.__TYPE_PRODUCTION__,
        2: RowItem.__TITLE__,
        3: RowItem.__PRICE_PURCHASE__,
        4: RowItem.__REST_COUNT__,
    },
    stop_words=[],
    file_templates=["price*.xls", "price*.xlsx"],
    sheet_indexes=[],
    row_item_adaptor=RowItem,
)


mark_up_provider = data_provider.MarkupRulesProviderFromUserConfig(
    autosnab_params.supplier.folder_name
)

autosnab_config = BasePriceParseConfigurationParams(
    markup_rules_provider=mark_up_provider,
    black_list_provider=data_provider.BlackListProviderFromUserConfig(),
    stop_words_provider=data_provider.StopWordsProviderFromUserConfig(),
    vendor_list=data_provider.VendorListProviderFromUserConfig(),
    manufacturer_aliases=data_provider.ManufacturerAliasesProviderFromUserConfig(),
    parser_params=autosnab_params,
)

autosnab_config = ParseConfiguration(autosnab_config)


class Autosnab54Parser(BaseParser):
    """
    logic for autosnab54_ru vendor
    """

    def process(self):
        """parse process"""
        res = super().process()
        for item in self.result:
            item.price_markup = item.price_opt

        return res

    @classmethod
    def get_min_rest_count(cls):
        """min rest count value for skip action"""
        return 0
