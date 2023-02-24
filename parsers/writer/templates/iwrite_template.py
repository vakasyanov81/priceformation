# -*- coding: utf-8 -*-
"""
write template interface
"""
__author__ = "Kasyanov V.A."


class IWriteTemplate:
    __EMPTY_COLUMN__ = "empty_column"

    """ write template interface """

    def exclude(self):
        """get exclude"""
        ex_field = "__EXCLUDE__"
        return getattr(self, ex_field) if hasattr(self, ex_field) else []

    def get_file_name(self):
        """get exclude"""
        file_field = "__FILE__"
        return (
            getattr(self, file_field)
            if hasattr(self, file_field)
            else "default_result.xls"
        )

    def columns(self):
        """get columns"""
        col_field = "__COLUMNS__"
        return getattr(self, col_field) if hasattr(self, col_field) else []

    def colors(self):
        """get colors"""
        col_field = "__COLOR__"
        return getattr(self, col_field) if hasattr(self, col_field) else {}
