# -*- coding: utf-8 -*-
"""
tests parse xlsx file
"""
__author__ = "Kasyanov V.A."

import pytest

from src.cfg import init_cfg

from src.parsers.xls_reader import __SKIPPED_EMPTY_ROW__, XlsReader

config = init_cfg()

_FILE_PATH = str(config.main.project_root) + "/tests/test_parsers/fixtures/price.xlsx"
_PARSE_PARAMS = {"start_row": 1, "columns": {0: "col_0", 1: "col_1"}}

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


@pytest.mark.parametrize(
    "sheets, rows_count, result",
    [
        ([0], 2, SHEET_1),
        ([0, 1], 4, SHEET_1 + SHEET_2),
        ([0, 1, 2], 6, SHEET_1 + SHEET_2 + SHEET_3),
    ],
)
def test_xls_rows_count_and_result(sheets, rows_count, result):
    """test rows count and result"""

    reader = make_reader()
    parse_res = reader.parse(sheets)

    assert len(parse_res) == rows_count
    assert reader.skipped_rows() == __SKIPPED_EMPTY_ROW__
    assert parse_res == result
