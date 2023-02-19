# -*- coding: utf-8 -*-
"""
# если разница между оптовой и розничной ценой составляет меньше 200р
# то делаем наценку 15% к оптовой цене
# наценка не должна превышать 1000р
"""
__author__ = "Kasyanov V.A."
from parsers.base_parser.base_parser import BaseParser
from parsers.row_item.row_item import RowItem
from parsers.vendors.zapaska_rest import ZapaskaRestParser

_SUPPLIER_FOLDER_NAME = "zapaska"


class ZapaskaPriceAndRestParser:
    """
    combine price parser and rest parser
    """
    __SUPPLIER_FOLDER_NAME__ = _SUPPLIER_FOLDER_NAME

    def __init__(self, price_config=None):
        self.price_config = price_config

    def get_result(self):
        """ get result """
        if not ZapaskaRestParser.is_active:
            return []
        parser = ZapaskaRestParser(price_mrp=self.get_price_mrp(), price_config=self.price_config)
        return parser.get_result()

    def get_price_mrp(self):
        """ get price mrp result """
        return ZapaskaParser(price_config=self.price_config).get_result()


class ZapaskaParser(BaseParser):
    """
    minimal recommended price
    """

    __SUPPLIER_FOLDER_NAME__ = _SUPPLIER_FOLDER_NAME
    __START_ROW__ = 7
    __SUPPLIER_NAME__ = "Запаска"
    __SUPPLIER_CODE__ = "2"

    __COLUMNS__ = {
        0: RowItem.__CODE__,
        1: RowItem.__CODE_ART__,
        2: RowItem.__TITLE__,
        5: RowItem.__PRICE_RECOMMENDED__
    }

    def after_process(self):
        pass
