# -*- coding: utf-8 -*-
"""
write price list interface
"""
__author__ = "Kasyanov V.A."


class IXlsDriver:
    """interface for write logic"""

    def add_sheet(self, sheet_name: str):
        """add sheet with sheet name"""
        raise NotImplementedError

    def write_head(self, names):
        """write head"""
        raise NotImplementedError

    def set_column_format(self, column_format: dict[int, str]):
        """
        set column format
        :param column_format: dict['column_name', '#,##0.00" ₽"']
        """
        raise NotImplementedError

    def write(self, i, j, _value, style=None, _color=None):
        """write"""
        raise NotImplementedError

    def save(self):
        """save file"""
        raise NotImplementedError

    def init_workbook(self, _folder: str, _file_name: str):
        """init workbook"""
        raise NotImplementedError
