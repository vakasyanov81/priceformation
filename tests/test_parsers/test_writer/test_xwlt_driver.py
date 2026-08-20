"""tests for openpyxl writer driver"""

from pathlib import Path
from typing import Any

import openpyxl
import pytest
from openpyxl.styles import Font

from parsers.writer.xwlt_driver import (
    WorkbookNotInitializedError,
    WorksheetNotInitializedError,
    XlsxWriterDriver,
    number_to_excel_column,
    solid_fill,
)

_COL_A = 1
_COL_Z = 26
_COL_AA = 27
_HEAD_A = "ColA"
_HEAD_B = "ColB"
_BODY_TEXT = "value"
_OTHER = "other"
_SHORT = "ab"
_FILL_HEX = "FFAA00"
_SHEET = "Prices"
_FILE_NAME = "out.xlsx"
_WIDTH_PAD = 4
_TEXT_FORMAT = "@"


def test_number_to_excel_column() -> None:
    """конвертация индекса колонки в букву Excel"""
    assert number_to_excel_column(_COL_A) == "A"
    assert number_to_excel_column(_COL_Z) == "Z"
    assert number_to_excel_column(_COL_AA) == "AA"
    assert number_to_excel_column(0) == ""


def test_xlsx_driver_starts_empty() -> None:
    driver = XlsxWriterDriver()
    assert driver.work_book is None
    assert driver.work_sheet is None
    assert driver.current_col_index == 0
    assert driver.current_row_index == 0
    assert driver.col_max_length == {}
    assert driver.row_index_at == 1
    assert driver._file_name is None


def test_xlsx_writer_full_cycle(tmp_path: Any) -> None:
    """создание книги, запись шапки/ячеек, формат и сохранение"""
    driver = XlsxWriterDriver()
    folder = f"{tmp_path}/"
    workbook = driver.init_workbook(folder, _FILE_NAME)

    assert workbook is driver.work_book
    assert driver.init_workbook(folder, _FILE_NAME) is workbook
    driver.add_sheet(_SHEET)
    assert driver.work_sheet is not None
    assert driver.work_sheet.title == _SHEET

    driver.write_head([_HEAD_A, _HEAD_B])
    body_style = Font(bold=True)
    fill_color = f"#{_FILL_HEX}"
    driver.write(1, 0, _BODY_TEXT, style=body_style, _color=fill_color)
    driver.write(1, 1, _OTHER)
    driver.write(2, 0, _SHORT)
    driver.set_column_format({_COL_A: _TEXT_FORMAT})
    assert driver.current_row_index == 3
    assert driver.current_col_index == 1
    driver.save()

    path = Path(tmp_path / _FILE_NAME)
    assert path.exists()
    assert driver.col_max_length[1] == len(_BODY_TEXT)
    assert driver.col_max_length[2] == len(_OTHER)
    _assert_saved_sheet(path)


def test_solid_fill_strips_hash_and_is_solid() -> None:
    hashed = solid_fill(f"#{_FILL_HEX}")
    plain = solid_fill(_FILL_HEX)
    assert hashed.fill_type == "solid"
    assert plain.fill_type == "solid"
    assert hashed.fgColor.rgb == plain.fgColor.rgb
    assert str(hashed.fgColor.rgb).endswith(_FILL_HEX)


def test_add_sheet_requires_workbook() -> None:
    with pytest.raises(WorkbookNotInitializedError):
        XlsxWriterDriver().add_sheet(_SHEET)


def test_write_requires_sheet() -> None:
    with pytest.raises(WorksheetNotInitializedError):
        XlsxWriterDriver().write(0, 0, _BODY_TEXT)


def test_set_column_format_requires_sheet() -> None:
    with pytest.raises(WorksheetNotInitializedError):
        XlsxWriterDriver().set_column_format({_COL_A: _TEXT_FORMAT})


def test_save_requires_sheet(tmp_path: Any) -> None:
    driver = XlsxWriterDriver()
    driver.init_workbook(f"{tmp_path}/", _FILE_NAME)
    with pytest.raises(WorkbookNotInitializedError):
        driver.save()


def test_save_requires_file_name(tmp_path: Any) -> None:
    driver = XlsxWriterDriver()
    driver.init_workbook(f"{tmp_path}/", _FILE_NAME)
    driver.add_sheet(_SHEET)
    driver._file_name = None
    with pytest.raises(WorkbookNotInitializedError):
        driver.save()


def _assert_saved_sheet(path: Path) -> None:
    sheet = openpyxl.load_workbook(path)[_SHEET]
    assert sheet["A1"].value == _HEAD_A
    assert sheet["B1"].value == _HEAD_B
    assert sheet["A1"].font.bold is True
    assert sheet["B1"].font.bold is True
    assert sheet["A2"].value == _BODY_TEXT
    assert sheet["B2"].value == _OTHER
    assert sheet["A3"].value == _SHORT
    assert sheet["A2"].font.bold is True
    assert sheet["B2"].font.bold is not True
    assert sheet["A2"].fill.patternType == "solid"
    assert str(sheet["A2"].fill.fgColor.rgb).endswith(_FILL_HEX)
    assert sheet.column_dimensions["A"].width == len(_BODY_TEXT) + _WIDTH_PAD
    assert sheet.column_dimensions["B"].width == len(_OTHER) + _WIDTH_PAD
    assert sheet.column_dimensions["A"].number_format == _TEXT_FORMAT
