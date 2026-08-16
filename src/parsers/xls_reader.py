"""
xls read logic
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, TypeAlias, cast

from python_calamine import CalamineWorkbook

import core
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
_MAX_ROWS = 10000

Row: TypeAlias = list[Any]
DRow: TypeAlias = dict[str, Any]

Sheet: TypeAlias = list[Row]
DSheet: TypeAlias = list[DRow]

IndexToHeader: TypeAlias = dict[int, str]
ParseParams: TypeAlias = dict[str, int | IndexToHeader]


class IXlsReader:
    """interface xls reader"""

    def parse(self, sheet_indexes: list[int] | None = None) -> DSheet:
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
    def get_instance(cls, file_path: str, reader_params: dict[str, Any]) -> "XlsReader":
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
        book = self.book
        if book is None or not book.sheet_names:
            core.make_raise("В прайсе отсутствуют вкладки!")
        workbook = cast(CalamineWorkbook, book)

        return [workbook.get_sheet_by_name(s_name).to_python(skip_empty_area=False) for s_name in workbook.sheet_names]

    def next_row_values(self, sheet: Sheet) -> Row | bool:
        """process for next xls row"""
        if is_end_row(self.cur_row_values, self.skipped_empty_rows):
            return False

        cols = sheet_cols(sheet)
        end_col = cols if cols <= self.reader_params.max_columns else self.reader_params.max_columns
        cur_row = self.cur_row
        self.cur_row += 1

        if self.cur_row > self.reader_params.max_rows:
            raise MaxRowsReached(self.reader_params.max_rows)

        try:
            self.cur_row_values = [strip_cell_value(cell) for cell in row_values(sheet, cur_row, end_col)]
        except IndexError:
            self.cur_row_values = [None]

        if is_empty_row(self.cur_row_values):
            self.skipped_empty_rows += 1
            return not is_end_row(self.cur_row_values, self.skipped_empty_rows)

        return self.cur_row_values

    def parse(self, sheet_indexes: list[int] | None = None) -> DSheet:
        """parse given sheets or all if not specified"""
        all_sheets = self.sheets()
        sheet_indexes = sheet_indexes or list(range(0, len(all_sheets)))
        rows: DSheet = []
        for sheet_index in sheet_indexes:
            self.skipped_empty_rows = 0
            self.cur_row = self.reader_params.start_row
            sheet = all_sheets[sheet_index]
            while self.next_row_values(sheet):
                if is_empty_row(self.cur_row_values):
                    continue
                rows.append(row_to_dict(self.cur_row_values or [], self.reader_params.columns))
        return rows


class MaxRowsReached(core.CoreExceptionError):
    """max rows reached exception"""

    def __init__(self, max_rows_count: int) -> None:
        super().__init__(f"maximum rows ({max_rows_count}) reached")
