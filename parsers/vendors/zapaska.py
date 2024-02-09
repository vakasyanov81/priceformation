# -*- coding: utf-8 -*-
"""
# если разница между оптовой и розничной ценой составляет меньше 200р
# то делаем наценку 15% к оптовой цене
# наценка не должна превышать 1000р
"""
__author__ = "Kasyanov V.A."

import dataclasses

from parsers import data_provider
from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.base_parser_config import (
    BasePriceParseConfigurationParams,
    ParseConfiguration,
)
from parsers.row_item.row_item import RowItem
from parsers.vendors.zapaska_rest import (
    ZapaskaRestParser,
    zapaska_rest_config,
    zapaska_rest_params,
)

_SUPPLIER_FOLDER_NAME = "zapaska"
_SUPPLIER_NAME = "Запаска"
_SUPPLIER_CODE = "2"


zapaska_params = dataclasses.replace(zapaska_rest_params)
zapaska_params.columns = {
    0: RowItem.__CODE__,
    1: RowItem.__CODE_ART__,
    2: RowItem.__TITLE__,
    5: RowItem.__PRICE_RECOMMENDED__,
}
zapaska_params.start_row = 7
zapaska_params.supplier_name = _SUPPLIER_NAME
zapaska_params.file_templates = ["price*.xls", "price*.xlsx"]


mark_up_provider = data_provider.MarkupRulesProviderFromUserConfig(
    zapaska_params.supplier.folder_name
)

zapaska_config = BasePriceParseConfigurationParams(
    markup_rules_provider=mark_up_provider,
    black_list_provider=data_provider.BlackListProviderFromUserConfig(),
    stop_words_provider=data_provider.StopWordsProviderFromUserConfig(),
    vendor_list=data_provider.VendorListProviderFromUserConfig(),
    manufacturer_aliases=data_provider.ManufacturerAliasesProviderFromUserConfig(),
    parser_params=zapaska_params,
)

zapaska_config = ParseConfiguration(zapaska_config)


class ZapaskaPriceAndRestParser:
    """
    combine price parser and rest parser
    """

    _parser = None

    def __init__(self, price_config=None):
        self.price_config = price_config

    def get_result(self):
        """get result"""
        if not ZapaskaRestParser.is_active:
            return []
        return ZapaskaRestParser(
            price_mrp=self.get_price_mrp(), parse_config=zapaska_rest_config
        ).parse()

    def get_price_mrp(self):
        """get price mrp result"""
        return ZapaskaParser(parse_config=self.price_config).parse()

    @classmethod
    def supplier_folder_name(cls):
        return zapaska_params.supplier.folder_name

    def parse(self):
        return self.get_result()


class ZapaskaParser(BaseParser):
    """
    minimal recommended price
    """

    def after_process(self):
        pass
