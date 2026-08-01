"""
write template interface
"""

from typing import Any

from parsers.writer.templates.column_helper import ColumnHelper


class IWriteTemplate:
    """interface for writing template"""

    __EMPTY_COLUMN__ = "empty_column"

    """ write template interface """

    def __init__(self) -> None:
        self._columns_formated: dict[str, ColumnHelper] | None = None

    def exclude(self) -> dict[str, Any]:
        """get exclude"""
        ex_field = "__EXCLUDE__"
        return getattr(self, ex_field) if hasattr(self, ex_field) else {}

    def get_file_name(self) -> str:
        """get exclude"""
        file_field = "__FILE__"
        return getattr(self, file_field) if hasattr(self, file_field) else "default_result.xls"

    def columns(self) -> list[dict[str, Any]]:
        """get columns"""
        col_field = "__COLUMNS__"
        return getattr(self, col_field) if hasattr(self, col_field) else []

    def colors(self) -> dict[str, Any]:
        """get colors"""
        col_field = "__COLOR__"
        return getattr(self, col_field) if hasattr(self, col_field) else {}

    def get_columns(self) -> dict[str, ColumnHelper]:
        """cached columns as ColumnHelper map"""
        if self._columns_formated is None:
            self._columns_formated = {}
            for column in self.columns():
                column_helper = ColumnHelper(column)
                self._columns_formated[column_helper.name] = column_helper
        return self._columns_formated

    def get_columns_format(self) -> dict[int, str]:
        """{1: "@ or 0.00 or ..."}"""
        formats = {}
        for index, col in enumerate(self.get_columns().values(), start=1):
            if col.format:
                formats[index] = col.format
        return formats
