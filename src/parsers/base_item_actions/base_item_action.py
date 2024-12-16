# -*- coding: utf-8 -*-
"""
base item action logic
"""
__author__ = "Kasyanov V.A."

from src.parsers.row_item.row_item import RowItem


class BaseItemAction:
    """Abstract base price item action"""

    # pylint: disable=R0903
    def __init__(self, item: RowItem):
        """init"""
        self.item = item

    def action(self):
        """action logic"""
        raise NotImplementedError
