# -*- coding: utf-8 -*-
"""
# greenstone
"""
__author__ = "Kasyanov V.A."
from parsers.base_parser.base_parser import BaseParser
from parsers.row_item.row_item import RowItem


class GreenstoneParser(BaseParser):
    """
     parser for Greenstone vendor
    """
    __SUPPLIER_FOLDER_NAME__ = 'greenstone'
    __START_ROW__ = 14
    __SUPPLIER_NAME__ = 'Greenstone'
    __SUPPLIER_CODE__ = '7'

    __COLUMNS__ = {
        1: RowItem.__CODE__,
        2: RowItem.__TITLE__,
        3: RowItem.__PRICE_PURCHASE__,
        4: RowItem.__REST_COUNT__
    }

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
