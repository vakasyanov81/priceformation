# -*- coding: utf-8 -*-
"""
logic for posh vendor
"""
__author__ = "Kasyanov V.A."

import re
from parsers.base_parser.base_parser import BaseParser, BasePriceParseConfiguration
from parsers.row_item.row_item import RowItem


class PoshkPriceParseConfiguration(BasePriceParseConfiguration):
    """ poshk price parser configuration """


class PoshkParser(BaseParser):
    """
    logic for posh vendor
    """
    __SUPPLIER_FOLDER_NAME__ = 'poshk'
    __START_ROW__ = 14
    __SUPPLIER_NAME__ = 'Пошк'
    __SUPPLIER_CODE__ = '1'

    __COLUMNS__ = {
        0: RowItem.__CODE__,
        1: RowItem.__TITLE__,
        2: RowItem.__PRICE_PURCHASE__,
        3: RowItem.__REST_COUNT__
    }

    def process(self):
        res = super().process()
        for item in self.result:
            self.add_price_markup(item)
            self.clear_and_set_title(item)
            item.title = self.prepare_title(item.title)
            self.set_type_production(item)

        return res

    def add_price_markup(self, item):
        """
        Добавить наценку
        """

        price = item.price_opt
        markup_percent = self.get_markup_percent(price)
        price = (markup_percent + 1) * price
        item.price_markup = self.round_price(price)
        item.percent_markup = markup_percent * 100

    def set_type_production(self, item):
        """
        Задать категорию
        """

        item.type_production = self.get_category_by_title(item.title)

    @classmethod
    def get_category_by_title(cls, title):
        """ get category name by title """
        title = title.lower()
        _available_categories = [
            'ободная лента',
            'шина',
            'покрышка',
            'камера',
            'диск'
        ]

        categories_map = {
            _available_categories[0]: "Ободная лента",
            _available_categories[1]: "Автошина",
            _available_categories[2]: "Автошина",
            _available_categories[3]: "Автокамера",
            _available_categories[4]: "Диск",
        }
        for av_category in _available_categories:
            if av_category in title:
                return categories_map[av_category]

        return "Разное"

    @classmethod
    def clear_and_set_title(cls, item):
        """ clear and set reared title """
        item.title = item.title.replace(', , шт', '').strip()

    @classmethod
    def _prepare_title_chunks(cls, chunks: list):
        """ get prepared title chunks """
        cls.replace_star_to_cross(chunks)
        cls.delete_white_spaces(chunks)
        return chunks

    @classmethod
    def replace_star_to_cross(cls, chunks: list):
        """
        ... 6.00*17.5 ... -> ... 6.00x17.5 ...
        :param chunks:
        :return:
        """
        _re_part_size = r'^\d+\.*\d*'
        for index, chunk in enumerate(chunks):
            if '*' not in chunk:
                continue
            if re.match(_re_part_size, chunk):
                chunks[index] = chunk.replace('*', 'x')

    @classmethod
    def delete_white_spaces(cls, chunks: list):
        """
        385/65  R22.5... -> 385/65R22.5...
        :param chunks:
        :return:
        """
        _re_part_size = r'R\d+.'  # R22.5 or R20
        if re.match(_re_part_size, chunks[1]):
            chunk = chunks.pop(1)
            chunks[0] += chunk
