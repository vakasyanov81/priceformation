"""Запись новых XLSX-книг через XlsxWriter с переиспользованием форматов."""

from pathlib import Path
from typing import Any

from xlsxwriter import Workbook
from xlsxwriter.format import Format
from xlsxwriter.worksheet import Worksheet

from parsers.writer.errors import WorkbookNotInitializedError, WorksheetNotInitializedError
from parsers.writer.ixlsx_driver import IXlsDriver

_WIDTH_PADDING = 4
_CHAR_PIXELS = 7
_COLUMN_PADDING_PIXELS = 5


class XlsxWriterAdapter(IXlsDriver):
    """Каждая книга владеет форматами; ширины и форматы колонок независимы у листов."""

    def __init__(self) -> None:
        self._book: Workbook | None = None
        self._sheet: Worksheet | None = None
        self._formats: dict[tuple[str, str, bool], Format] = {}
        self._columns: dict[int, str] = {}
        self._widths: dict[int, int] = {}

    def init_workbook(self, _folder: str, _file_name: str) -> Workbook:
        """Открыть книгу; URL остаются текстом, как в прежнем драйвере."""
        if self._book is None:
            path = str(Path(_folder) / _file_name)
            self._book = Workbook(path, {'strings_to_urls': False})
        return self._book

    def add_sheet(self, sheet_name: str) -> XlsxWriterAdapter:
        """Добавить независимый лист, включая лист без строк."""
        if self._book is None:
            raise WorkbookNotInitializedError()
        self._sheet = self._book.add_worksheet(sheet_name)
        self._columns = {}
        self._widths = {}
        return self

    def write_head(self, names: list[str], row: int = 0) -> None:
        """Записать жирную шапку без создания формата для каждой ячейки."""
        for col, name in enumerate(names):
            self.write(row, col, name, style=True)

    def set_column_format(self, column_format: dict[int, str]) -> None:
        """Индексы колонок в шаблонах начинаются с единицы."""
        if self._sheet is None or self._book is None:
            raise WorksheetNotInitializedError()
        self._columns.update(column_format)
        for index, number_format in column_format.items():
            col = index - 1
            cell_format = _cell_format(self._book, self._formats, number_format)
            self._sheet.set_column(col, col, None, cell_format)

    def write(
        self,
        row_idx: int,
        col_idx: int,
        cell_content: Any,
        style: Any = None,
        _color: str | None = None,
    ) -> None:
        """Записать ячейку, сохранив числовой формат под заливкой."""
        if self._sheet is None or self._book is None:
            raise WorksheetNotInitializedError()
        number_format = self._columns.get(col_idx + 1, 'General')
        bold = bool(style)
        cell_format = _cell_format(self._book, self._formats, number_format, _color or '', bold)
        status = self._sheet.write(row_idx, col_idx, cell_content, cell_format)
        if status:
            raise ValueError(f'Не удалось записать ячейку ({row_idx}, {col_idx}): {status}')
        length = len(str(cell_content or ''))
        _update_width(
            self._sheet, self._widths, col_idx, length, _cell_format(self._book, self._formats, number_format)
        )

    def save(self) -> None:
        """Сериализовать и закрыть книгу."""
        if self._book is None or self._sheet is None:
            raise WorkbookNotInitializedError()
        self._book.close()


def _cell_format(
    book: Workbook,
    cache: dict[tuple[str, str, bool], Format],
    number_format: str,
    color: str = '',
    bold: bool = False,
) -> Format:
    """Переиспользовать комбинацию формата числа, заливки и жирности внутри книги."""
    key = (number_format, color, bold)
    cached = cache.get(key)
    if cached is None:
        properties: dict[str, Any] = {'num_format': number_format, 'bold': bold}
        if color:
            properties['bg_color'] = color
        cached = book.add_format(properties)
        cache[key] = cached
    return cached


def _update_width(
    sheet: Worksheet,
    widths: dict[int, int],
    column: int,
    length: int,
    cell_format: Format,
) -> None:
    """Компенсировать добавляемый XlsxWriter отступ, сохранив прежнюю ширину."""
    if length <= widths.get(column, -1):
        return
    widths[column] = length
    width = length + _WIDTH_PADDING - _COLUMN_PADDING_PIXELS / _CHAR_PIXELS
    sheet.set_column(column, column, width, cell_format)
