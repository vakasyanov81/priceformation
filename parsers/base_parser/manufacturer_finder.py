# -*- coding: utf-8 -*-
"""
find manufacturer, make correct manufacturer in title
"""
__author__ = "Kasyanov V.A."

from parsers.base_parser.alias_container import AliasContainer
from parsers.base_parser.base_finder import BaseFinder
from parsers.row_item.row_item import RowItem


class ManufacturerFinder:
    """
    find manufacturer, make correct manufacturer in title
    """

    def __init__(self, aliases: dict = None):
        """init"""
        self.aliases = AliasContainer(aliases)
        self._finder = BaseFinder(self.aliases)

    def process(self, item):
        """process"""

        manufacturer, bad_manufacturer = self._finder.find_word_in_title(item.title)

        if bad_manufacturer and manufacturer:
            self._finder.replace_alias_in_title(item, bad_manufacturer, manufacturer)

        # replace manufacturer
        if manufacturer:
            item.manufacturer = manufacturer
        elif item.manufacturer:
            self.correction_manufacturer(item)

    def correction_manufacturer(self, rec: RowItem):
        """correction manufacturer"""
        self._finder.correction_field(
            rec, field_name="manufacturer", aliases=self.aliases
        )
