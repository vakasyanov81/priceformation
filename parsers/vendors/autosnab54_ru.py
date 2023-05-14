# -*- coding: utf-8 -*-
"""
logic for autosnab54_ru vendor
"""
__author__ = "Kasyanov V.A."

from parsers.base_parser.base_parser import BaseParser
from parsers.row_item.row_item import RowItem


class Autosnab54Parser(BaseParser):
    """
    logic for autosnab54_ru vendor
    """

    _SUPPLIER_FOLDER_NAME = "autosnab54_ru"
    __START_ROW__ = 2
    _SUPPLIER_NAME = "Автоснабжение"
    __SUPPLIER_CODE__ = "6"

    __COLUMNS__ = {
        0: RowItem.__TYPE_PRODUCTION__,
        2: RowItem.__TITLE__,
        3: RowItem.__PRICE_PURCHASE__,
        4: RowItem.__REST_COUNT__,
    }

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
