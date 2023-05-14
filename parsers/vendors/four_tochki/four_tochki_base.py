# -*- coding: utf-8 -*-
"""
base logic for four_tochki vendor
"""
__author__ = "Kasyanov V.A."

from parsers.base_parser.base_parser import BaseParser, ParserParams
from parsers.row_item.vendors.row_item_mim import RowItemMim

fourtochki_params = ParserParams(
    supplier_folder_name="four_tochki",
    start_row=2,
    supplier_name="Форточки",
    supplier_code="5",
    sheet_info="",
    columns={},
    stop_words=[],
    file_templates=["price*.xls", "price*.xlsx"],
    sheet_indexes=[],
    row_item_adaptor=RowItemMim,
)


class FourTochkiParserBase(BaseParser):
    """
    base logic for four_tochki vendor
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
