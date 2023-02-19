# -*- coding: utf-8 -*-
"""
base logic for four_tochki vendor
"""
__author__ = "Kasyanov V.A."

from parsers.base_parser.base_parser import BaseParser
from parsers.row_item.vendors.row_item_mim import RowItemMim


class FourTochkiParserBase(BaseParser):
    """
    base logic for four_tochki vendor
    """
    __SUPPLIER_FOLDER_NAME__ = "four_tochki"
    __START_ROW__ = 2
    __SUPPLIER_NAME__ = "Форточки"
    __SUPPLIER_CODE__ = "5"

    __ROW_ITEM_ADAPTOR__ = RowItemMim

    @classmethod
    def get_current_category(cls):
        """ getting current category """
        raise NotImplementedError()

    @classmethod
    def set_category(cls, item):
        """ set category to row price item """
        item.type_production = cls.get_current_category()

    def process(self):
        """ parse process """
        res = super().process()
        for item in self.result:
            self.add_price_markup(item)
            self.skip_by_min_rest(item)
            self.set_category(item)
            self.correction_category(item)
        return res
