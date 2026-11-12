"""Колонки шаблона и их представление для драйвера записи."""

from typing import Any, ClassVar

from parsers.writer.templates.column_helper import ColumnHelper
from parsers.writer.templates.group_output import WriteColumns


class TemplateColumns:
    """Настройки колонок и локальный кэш их разбора."""

    __COLUMNS__: ClassVar[WriteColumns] = []

    def __init__(self) -> None:
        self._columns_formated: dict[str, ColumnHelper] | None = None

    def columns(self) -> list[dict[str, Any]]:
        """get columns"""
        return list(self.__COLUMNS__)

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
