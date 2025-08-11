# -*- coding: utf-8 -*-
"""
helper for write-column structure
"""
__author__ = "Kasyanov V.A."


class ColumnHelper:
    """
    helper for write-column structure
    """

    def __init__(self, col: dict):
        """
        dict with column name and info
        :param col:
        {
            "Тип товара": {
                "style": {
                    "width": 256 * 15
                },
                "field": RowItem.__TYPE_PRODUCTION__
            }
        }
        """
        self._col = col

    @property
    def column(self):
        """
        dict with column info
        :return:
        {
            "style": {
                "width": 256 * 15
            },
            "field": RowItem.__TYPE_PRODUCTION__
        }
        """
        return list(self._col.values())[0]

    @property
    def name(self):
        """
        column name
        :return: "Тип товара"
        """
        return list(self._col.keys())[0]

    @property
    def style(self):
        """column style"""
        return self.column.get("style") or {}

    @property
    def style_width(self):
        """column width"""
        return self.style.get("width")

    @property
    def def_value(self):
        """default value"""
        return self.column.get("default_value")

    @property
    def field(self):
        """filed name in data-row for write"""
        return self.column.get("field")

    @property
    def skip(self) -> bool:
        """if True, then skip column"""
        return bool(self.column.get("skip"))
