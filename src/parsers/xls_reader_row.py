"""Row helpers for xls reader."""

from typing import Any

from python_calamine import CalamineWorkbook

Row = list[Any]
Sheet = list[Row]
DRow = dict[str, Any]
IndexToHeader = dict[int, str]

__SKIPPED_EMPTY_ROW__ = 10


def open_book(file_path: str) -> CalamineWorkbook:
    """open book"""
    return CalamineWorkbook.from_path(file_path)


def row_values(sheet: Sheet, cur_row: int, end_col: int) -> Row:
    return sheet[cur_row][:end_col]


def sheet_cols(sheet: Sheet) -> int:
    return len(sheet[0])


def strip_cell_value(cell_value: str | Any) -> str | Any:
    return cell_value.strip() if isinstance(cell_value, str) else cell_value


def row_to_dict(row: Row, columns: IndexToHeader) -> DRow:
    """row to dict by column mapping"""
    row_dict: dict[str, Any] = {}
    for col_number in columns:
        row_dict[str(columns.get(col_number))] = row[col_number]
    return row_dict


def is_empty_row(cur_row_values: Row | None) -> bool:
    """row is empty?"""
    return not any(cur_row_values or [])


def is_end_row(cur_row_values: Row | None, skipped_empty_rows: int) -> bool:
    """is end row?"""
    return is_empty_row(cur_row_values) and skipped_empty_rows >= __SKIPPED_EMPTY_ROW__
