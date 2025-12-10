"""
xls read logic
"""

# pylint: disable=missing-function-docstring

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, TypeAlias

from python_calamine import CalamineWorkbook

import core
from cfg import init_cfg

_MAX_COLUMNS = 50
_MAX_ROWS = 10000
__SKIPPED_EMPTY_ROW__ = 10

Row: TypeAlias = list[Any]
DRow: TypeAlias = dict[str, Any]

Sheet: TypeAlias = list[Row]
DSheet: TypeAlias = list[DRow]

IndexToHeader: TypeAlias = dict[int, str]
ParseParams: TypeAlias = dict[str, int | IndexToHeader]

init_cfg()


class IXlsReader:
    """interface xls reader"""

    # pylint: disable=R0903

    def parse(self, sheet_indexes: list | None = None):
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
    def get_instance(cls, file_path: str, params: dict[str, Any]) -> 'XlsReader':
        """get instance XlsReader / XlsxReader"""
        if not Path(file_path).exists():
            raise FileNotFoundError
        return cls(file_path, params)

    def __init__(self, file_path: str, params: dict[str, Any]):
        """init"""
        self.cur_row_values: Row | None = None
        self._skipped_empty_rows = 0
        self.book: CalamineWorkbook | None = None
        self.params: ParamsHelper = ParamsHelper(**params)
        self.open_book(file_path)

    def open_book(self, file_path: str) -> None:
        """open book"""
        self.book = self._open_book(file_path)

    @classmethod
    def _open_book(cls, file_path: str) -> CalamineWorkbook:
        """open book"""
        return CalamineWorkbook.from_path(file_path)

    def skipped_rows(self) -> int:
        """get skipped rows count value"""
        return self._skipped_empty_rows

    def get_sheet_names(self) -> list[str]:
        """get sheet names"""
        return self.book.sheet_names if self.book else []

    def get_sheet_by_name(self, s_name: str) -> Sheet:
        """get sheet by name"""
        return self.book.get_sheet_by_name(s_name).to_python(skip_empty_area=False) if self.book else []

    def sheets(self) -> list[Sheet]:
        """get sheet list"""

        if not self.get_sheet_names():
            core.make_raise("В прайсе отсутствуют вкладки!")

        return [self.get_sheet_by_name(s_name) for s_name in self.get_sheet_names()]

    def next_row_values(self, sheet: Sheet) -> Row | bool:
        """process for next xls row"""

        def _strip_cell_value(cell_value: str | Any) -> str | Any:
            return cell_value.strip() if isinstance(cell_value, str) else cell_value

        if self.is_end_row():
            return False

        end_col = (
            self.sheet_cols(sheet) if self.sheet_cols(sheet) <= self.params.max_columns else self.params.max_columns
        )
        cur_row = self.cur_row
        self.cur_row += 1

        if self.cur_row > self.params.max_rows:
            raise MaxRowsReached(self.params.max_rows)

        try:
            self.cur_row_values = [_strip_cell_value(cell) for cell in self.row_values(sheet, cur_row, end_col)]
        except IndexError:
            self.cur_row_values = [None]

        if self.is_empty_row():
            self._skipped_empty_rows += 1
            return not self.is_end_row()

        return self.cur_row_values

    @classmethod
    def row_values(cls, sheet: Sheet, cur_row: int, end_col: int) -> Row:
        return sheet[cur_row][0:end_col]

    @classmethod
    def sheet_cols(cls, sheet: Sheet) -> int:
        return len(sheet[0])

    def _get_cur_row_values(self) -> Row:
        return self.cur_row_values or list()

    def is_empty_row(self) -> bool:
        """row is empty?"""
        for value in self._get_cur_row_values():
            if value:
                return False
        return True

    def is_end_row(self) -> bool:
        """is end row?"""
        return self.is_empty_row() and self._skipped_empty_rows >= __SKIPPED_EMPTY_ROW__

    def parse(self, sheet_indexes: list[int] | None = None) -> DSheet:
        """parse given sheets or all if not specified"""
        rows = []

        all_num_sheets = len(self.sheets())

        sheet_indexes = sheet_indexes or list(range(0, all_num_sheets))

        for sheet_index in sheet_indexes:
            self._skipped_empty_rows = 0
            self.cur_row = self.params.start_row
            rows += self.parse_sheet(self.sheets()[sheet_index])

        return rows

    def parse_sheet(self, sheet: Sheet) -> DSheet:
        """parse sheet"""
        rows: list[dict[str, Any]] = []
        while self.next_row_values(sheet):
            if self.is_empty_row():
                continue
            rows.append(self.to_dict(self._get_cur_row_values()))

        return rows

    def to_dict(self, row: Row) -> DRow:
        """row to dict"""

        result: dict[str, Any] = {}
        col_numbers = list(self.params.columns.keys())
        for col_number in col_numbers:
            val = row[col_number]
            col_name = str(self.params.columns.get(col_number))
            result[col_name] = val

        return result


class MaxRowsReached(core.CoreExceptionError):  # type: ignore
    """max rows reached exception"""

    def __init__(self, max_rows_count: int) -> None:
        super().__init__(f"maximum rows ({max_rows_count}) reached")
