# -*- coding: utf-8 -*-
"""
write template interface
"""
__author__ = "Kasyanov V.A."

from parsers.writer.templates.column_helper import ColumnHelper


class IWriteTemplate:
    """interface for writing template"""

    __EMPTY_COLUMN__ = "empty_column"

    """ write template interface """

    def __init__(self):
        self._columns_formated: dict[str, ColumnHelper] | None = None
        self._column_names: list[str] | None = None

    def exclude(self):
        """get exclude"""
        ex_field = "__EXCLUDE__"
        return getattr(self, ex_field) if hasattr(self, ex_field) else []

    def get_file_name(self):
        """get exclude"""
        file_field = "__FILE__"
        return getattr(self, file_field) if hasattr(self, file_field) else "default_result.xls"

    def columns(self) -> list[dict]:
        """get columns"""
        col_field = "__COLUMNS__"
        return getattr(self, col_field) if hasattr(self, col_field) else []

    def colors(self):
        """get colors"""
        col_field = "__COLOR__"
        return getattr(self, col_field) if hasattr(self, col_field) else {}

    def get_columns(self) -> dict[str, ColumnHelper]:
        if self._columns_formated is None:
            self._columns_formated = {}
            for column in self.columns():
                _c = ColumnHelper(column)
                self._columns_formated[_c.name] = _c
        return self._columns_formated

    def get_column_names(self) -> list[str]:
        if self._column_names is None:
            self._column_names = []
            for name, _ in self.get_columns().items():
                self._column_names.append(name)
        return self._column_names

    def get_column_index(self, name: str) -> int:
        return self.get_column_names().index(name) + 1

    def get_columns_format(self) -> dict[int, str]:
        """{1: "@ or 0.00 or ..."}"""
        return {self.get_column_index(c_title): col.format for c_title, col in self.get_columns().items() if col.format}
