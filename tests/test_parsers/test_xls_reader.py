"""
tests parse xlsx file
"""

import pytest

from cfg import init_cfg
from parsers.xls_reader import __SKIPPED_EMPTY_ROW__, XlsReader

config = init_cfg()

_FILE_PATH = str(config.main.project_root) + "/tests/test_parsers/fixtures/price.xlsx"
_OLD_FILE_PATH = str(config.main.project_root) + "/tests/test_parsers/fixtures/price_old.xls"
_PIONER_FILE_PATH = str(config.main.project_root) + "/tests/test_parsers/fixtures/price_pioner.xlsx"
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


def make_reader():
    """make reader"""
    return XlsReader.get_instance(_FILE_PATH, _PARSE_PARAMS)


def make_old_reader():
    """make old reader"""
    return XlsReader.get_instance(_OLD_FILE_PATH, _PARSE_PARAMS)


@pytest.mark.parametrize(
    "sheets, rows_count, result, reader",
    [
        ([0], 2, SHEET_1, make_reader()),
        ([0, 1], 4, SHEET_1 + SHEET_2, make_reader()),
        ([0, 1, 2], 6, SHEET_1 + SHEET_2 + SHEET_3, make_reader()),
        ([0], 2, SHEET_1, make_old_reader()),
        ([0, 1], 4, SHEET_1 + SHEET_2, make_old_reader()),
        ([0, 1, 2], 6, SHEET_1 + SHEET_2 + SHEET_3, make_old_reader()),
    ],
)
def test_xls_rows_count_and_result(sheets, rows_count, result, reader):
    """test rows count and result"""
    parse_res = reader.parse(sheets)

    assert len(parse_res) == rows_count
    assert reader.skipped_rows() == __SKIPPED_EMPTY_ROW__
    assert parse_res == result


def test_xlsx_with_skipped_first_column():
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
