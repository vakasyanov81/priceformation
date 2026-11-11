"""
xls read logic
"""

from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

from python_calamine import CalamineWorkbook

from domain.exceptions import CoreExceptionError, make_raise
from parsers.raw_table import RawRow, RawTable
from parsers.xls_reader_row import (
    is_empty_row,
    is_end_row,
    open_book,
    row_to_dict,
    row_values,
    sheet_cols,
    strip_cell_value,
)

_MAX_COLUMNS = 50
_MAX_ROWS = 100_000

type Row = list[Any]
type DRow = dict[str, Any]

type Sheet = list[Row]
type DSheet = list[DRow]

type IndexToHeader = dict[int, str]
type ParseParams = dict[str, int | IndexToHeader]


class IXlsReader:
    """interface xls reader"""

    def parse(self, sheet_indexes: Sequence[int] | None = None) -> DSheet:
        """do parse"""
        raise NotImplementedError


@dataclass
class ParamsHelper:
    """params data container"""

    start_row: int = field(default=0)
    cur_row: int = field(default=0)
    max_columns: int = field(default=_MAX_COLUMNS)
    max_rows: int = field(default=_MAX_ROWS)
    # mapping columns. {0: "title", 1: "price"...}
    columns: IndexToHeader = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.cur_row = self.cur_row or self.start_row


class XlsReader(IXlsReader):
    """xls reader"""

    @classmethod
    def get_instance(cls, file_path: str, reader_params: dict[str, Any]) -> XlsReader:
        """get instance XlsReader / XlsxReader"""
        if not Path(file_path).exists():
            raise FileNotFoundError
        return cls(file_path, reader_params)

    def __init__(self, file_path: str, reader_params: dict[str, Any]):
        """init"""
        self.cur_row_values: Row | None = None
        self.cur_row = 0
        self.skipped_empty_rows = 0
        self.book: CalamineWorkbook | None = open_book(file_path)
        self.reader_params: ParamsHelper = ParamsHelper(**reader_params)

    def sheets(self) -> list[Sheet]:
        """get sheet list"""
        return [self._load_sheet(s_name) for s_name in self._sheet_names()]

    def _sheet_names(self) -> list[str]:
        """Имена вкладок книги; книга без вкладок — ошибка."""
        book = self.book
        if book is None or not book.sheet_names:
            make_raise('В прайсе отсутствуют вкладки!')
        return cast(CalamineWorkbook, book).sheet_names

    def _load_sheet(self, sheet_name: str) -> Sheet:
        """Прочитать одну вкладку: разбор листа — самое дорогое в чтении xlsx."""
        workbook = cast(CalamineWorkbook, self.book)
        return workbook.get_sheet_by_name(sheet_name).to_python(skip_empty_area=False)

    def next_row_values(self, sheet: Sheet) -> Row | bool:
        """process for next xls row"""
        if is_end_row(self.cur_row_values, self.skipped_empty_rows):
            return False

        cols = sheet_cols(sheet)
        end_col = cols if cols <= self.reader_params.max_columns else self.reader_params.max_columns
        cur_row = self.cur_row
        self.cur_row += 1

        if self.cur_row > self.reader_params.max_rows:
            raise MaxRowsReachedError(self.reader_params.max_rows)

        if cur_row < len(sheet):
            self.cur_row_values = [strip_cell_value(cell) for cell in row_values(sheet, cur_row, end_col)]
        else:
            # за последней строкой листа: считается пустой, после серии пустых чтение завершается
            self.cur_row_values = [None]

        if is_empty_row(self.cur_row_values):
            self.skipped_empty_rows += 1
            return not is_end_row(self.cur_row_values, self.skipped_empty_rows)

        return self.cur_row_values

    def parse(self, sheet_indexes: Sequence[int] | None = None) -> DSheet:
        """parse given sheets or all if not specified

        Читаются только запрошенные вкладки: у МИМ три поставщика на одной книге,
        и каждый иначе разбирал бы все листы, включая самый большой чужой.
        """
        sheet_names = self._sheet_names()
        sheet_indexes = sheet_indexes or list(range(len(sheet_names)))
        rows: DSheet = []
        for sheet_index in sheet_indexes:
            self.skipped_empty_rows = 0
            self.cur_row = self.reader_params.start_row
            sheet = self._load_sheet(sheet_names[sheet_index])
            while self.next_row_values(sheet):
                if is_empty_row(self.cur_row_values):
                    continue
                rows.append(row_to_dict(self.cur_row_values or [], self.reader_params.columns))
        return rows


class MaxRowsReachedError(CoreExceptionError):
    """max rows reached exception"""

    def __init__(self, max_rows_count: int) -> None:
        super().__init__(f'maximum rows ({max_rows_count}) reached')


def read_raw_tables(reader: XlsReader, sheet_indexes: Sequence[int]) -> list[RawTable]:
    """Прочитать выбранные листы без strip и отображения колонок."""
    sheet_names = reader._sheet_names()
    selected = sheet_indexes or list(range(len(sheet_names)))
    return [_raw_table(reader, index, sheet_names[index]) for index in selected]


def _raw_table(reader: XlsReader, sheet_index: int, sheet_name: str) -> RawTable:
    sheet = reader._load_sheet(sheet_name)
    if len(sheet) > reader.reader_params.max_rows:
        raise MaxRowsReachedError(reader.reader_params.max_rows)
    end_col = min(sheet_cols(sheet), reader.reader_params.max_columns) if sheet else 0
    rows = []
    for row_number, source_row in enumerate(sheet, start=1):
        rows.append(_raw_row(source_row[:end_col], row_number))
    return RawTable(sheet_index=sheet_index, rows=tuple(rows))


def _raw_row(source_row: Row, row_number: int) -> RawRow:
    fields = {str(column): cell for column, cell in enumerate(source_row)}
    return RawRow(fields, row_number)
