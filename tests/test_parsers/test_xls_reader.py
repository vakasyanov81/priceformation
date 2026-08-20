"""
tests parse xlsx file
"""

from typing import Any

import pytest

from cfg import init_cfg
from parsers.xls_reader import MaxRowsReached, XlsReader
from parsers.xls_reader_row import __SKIPPED_EMPTY_ROW__

config = init_cfg()

_PROJECT_ROOT = str(config.main.project_root)
_FILE_PATH = f"{_PROJECT_ROOT}/tests/test_parsers/fixtures/price.xlsx"
_OLD_FILE_PATH = f"{_PROJECT_ROOT}/tests/test_parsers/fixtures/price_old.xls"
_PIONER_FILE_PATH = f"{_PROJECT_ROOT}/tests/test_parsers/fixtures/price_pioner.xlsx"
_PARSE_PARAMS = {"start_row": 1, "columns": {0: "col_0", 1: "col_1"}}

_PIONER_PARSE_PARAMS = {
    "start_row": 12,
    "columns": {1: "c1", 2: "c2", 4: "c4", 5: "c5"},
}

SHEET_1 = [
    {"col_0": 87674341266.0, "col_1": "CROSSLEADER  225/40/18  Y 92 DSU02"},
    {
        "col_0": 88538061200.0,
        "col_1": "HIFLY  185/60/14  T 82 Win-turi 212  старше 3-х лет",
    },
]

SHEET_2 = [
    {"col_0": 89311526789.0, "col_1": "GoodNord 315/70R22.5 BAND"},
    {"col_0": 89217774527.0, "col_1": "GoodNord 315/70R22.5"},
]

SHEET_3 = [
    {
        "col_0": 86015679120.0,
        "col_1": "LEMMERZ  11,75\\R22,5 10*335 ET0  d281  [2920687 alive]",
    },
    {
        "col_0": 86348478178.0,
        "col_1": "LEMMERZ  11,75\\R22,5 10*335 ET120  d281  [2920695 alive]",
    },
]


def make_reader() -> XlsReader:
    """make reader"""
    return XlsReader.get_instance(_FILE_PATH, _PARSE_PARAMS)


def make_old_reader() -> XlsReader:
    """make old reader"""
    return XlsReader.get_instance(_OLD_FILE_PATH, _PARSE_PARAMS)


@pytest.mark.parametrize(
    "sheets, rows_count, expected_rows, reader",
    [
        ([0], 2, SHEET_1, make_reader()),
        ([0, 1], 4, SHEET_1 + SHEET_2, make_reader()),
        ([0, 1, 2], 6, SHEET_1 + SHEET_2 + SHEET_3, make_reader()),
        ([0], 2, SHEET_1, make_old_reader()),
        ([0, 1], 4, SHEET_1 + SHEET_2, make_old_reader()),
        ([0, 1, 2], 6, SHEET_1 + SHEET_2 + SHEET_3, make_old_reader()),
    ],
)
def test_xls_rows_count_and_result(sheets: Any, rows_count: Any, expected_rows: Any, reader: Any) -> None:
    """test rows count and result"""
    parse_res = reader.parse(sheets)

    assert len(parse_res) == rows_count
    assert reader.skipped_empty_rows == __SKIPPED_EMPTY_ROW__
    assert parse_res == expected_rows


def test_xlsx_with_skipped_first_column() -> None:
    """test rows count and result"""
    reader = XlsReader.get_instance(_PIONER_FILE_PATH, _PIONER_PARSE_PARAMS)
    parse_res = reader.parse([0])

    assert len(parse_res) == 2
    assert parse_res[0] == {
        "c1": "Автокамера 16.9-24",
        "c2": 5000.0,
        "c4": 16.0,
        "c5": "",
    }
    assert parse_res[1] == {
        "c1": "Автокамера 16.9-28",
        "c2": 5500.0,
        "c4": 16.0,
        "c5": "",
    }


def test_xls_reader_stores_parse_params() -> None:
    reader = make_reader()
    assert reader.reader_params.columns == _PARSE_PARAMS["columns"]
    assert reader.reader_params.start_row == _PARSE_PARAMS["start_row"]
    assert reader.cur_row == 0
    assert reader.skipped_empty_rows == 0


def _row_reader(**reader_params: Any) -> XlsReader:
    merged = {"start_row": 0, "columns": {0: "col_0"}, **reader_params}
    reader = XlsReader.get_instance(_FILE_PATH, merged)
    reader.cur_row = 0
    reader.skipped_empty_rows = 0
    reader.cur_row_values = None
    return reader


def test_next_row_values_truncates_to_max_columns() -> None:
    reader = _row_reader(max_columns=2)
    assert reader.next_row_values([["a", "b", "c"]]) == ["a", "b"]


def test_next_row_values_allows_exactly_max_rows() -> None:
    reader = _row_reader(max_rows=2)
    sheet = [["a"], ["b"], ["c"]]
    assert reader.next_row_values(sheet) == ["a"]
    assert reader.next_row_values(sheet) == ["b"]
    with pytest.raises(MaxRowsReached):
        reader.next_row_values(sheet)


def _read_until_end(reader: XlsReader, sheet: list[Any]) -> list[Any]:
    collected: list[Any] = []
    nxt: Any = True
    while nxt:
        nxt = reader.next_row_values(sheet)
        if isinstance(nxt, list):
            collected.append(nxt)
    return collected


def _blank_then_data(data_row: list[Any], empty_count: int = 6) -> list[list[Any]]:
    rows: list[list[Any]] = []
    while len(rows) < empty_count:
        rows.append([None])
    rows.append(data_row)
    return rows


def test_next_row_values_counts_empty_rows_by_one() -> None:
    reader = _row_reader()
    assert _read_until_end(reader, _blank_then_data(["data"])) == [["data"]]


def test_parse_resets_skipped_empty_rows() -> None:
    reader = _row_reader(max_rows=1)
    reader.skipped_empty_rows = 5

    def fake_sheets() -> list[Any]:
        return [[["a"], ["b"]]]

    reader.sheets = fake_sheets  # type: ignore[method-assign]
    with pytest.raises(MaxRowsReached):
        reader.parse([0])
    assert reader.skipped_empty_rows == 0
