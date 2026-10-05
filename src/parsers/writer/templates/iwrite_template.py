"""
write template interface
"""

from typing import Any, ClassVar

from parsers.writer.templates.column_helper import ColumnHelper

type WriteColumns = list[dict[str, Any]]
type WriteColors = dict[str, Any]
type WriteExclude = dict[str, Any]

# Настройки, которые шаблон задаёт классом. Имена в __COLUMNS__-стиле придуманы
# исторически, но новые опечатки в них ловятся на импорте, а не на записи
# файла: см. IWriteTemplate.
DEFAULT_TEMPLATE_FILE = 'default_result.xls'
EMPTY_COLUMN = 'empty_column'


class IWriteTemplate:
    """interface for writing template

    Настройки объявлены явно, с пустыми дефолтами: подкласс, который задал
    `__COLUMNS__` с опечаткой, падает на импорте (нет такого поля), а не
    молча пишет файл без колонок.
    """

    __EMPTY_COLUMN__ = EMPTY_COLUMN

    __COLUMNS__: ClassVar[WriteColumns] = []
    __FILE__: ClassVar[str] = DEFAULT_TEMPLATE_FILE
    __EXCLUDE__: ClassVar[WriteExclude] = {}
    __COLOR__: ClassVar[WriteColors] = {}

    """ write template interface """

    def __init__(self) -> None:
        self._columns_formated: dict[str, ColumnHelper] | None = None

    def exclude(self) -> dict[str, Any]:
        """get exclude"""
        return dict(self.__EXCLUDE__)

    def get_file_name(self) -> str:
        """get file name pattern"""
        return self.__FILE__

    def columns(self) -> list[dict[str, Any]]:
        """get columns"""
        return list(self.__COLUMNS__)

    def colors(self) -> dict[str, Any]:
        """get colors"""
        return dict(self.__COLOR__)

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
