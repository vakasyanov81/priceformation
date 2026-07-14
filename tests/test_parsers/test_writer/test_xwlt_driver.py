"""tests for openpyxl writer driver"""

from pathlib import Path

from openpyxl.styles import Font

from parsers.writer.xwlt_driver import XlsxWriterDriver

_COL_A = 1
_COL_Z = 26
_COL_AA = 27


def test_number_to_excel_column():
    """конвертация индекса колонки в букву Excel"""
    assert XlsxWriterDriver.number_to_excel_column(_COL_A) == "A"
    assert XlsxWriterDriver.number_to_excel_column(_COL_Z) == "Z"
    assert XlsxWriterDriver.number_to_excel_column(_COL_AA) == "AA"
    assert XlsxWriterDriver.number_to_excel_column(0) == ""


def test_xlsx_writer_full_cycle(tmp_path):
    """создание книги, запись шапки/ячеек, формат и сохранение"""
    driver = XlsxWriterDriver()
    folder = f"{tmp_path}/"
    file_name = "out.xlsx"
    workbook = driver.init_workbook(folder, file_name)

    assert workbook is driver.get_workbook()
    assert driver.init_workbook(folder, file_name) is workbook

    driver.add_sheet("Prices")
    assert driver.work_sheet.title == "Prices"

    driver.write_head(["ColA", "ColB"])
    driver.write(1, 0, "value", style=Font(bold=True), _color="#FFAA00")
    driver.write(1, 1, None)
    driver.set_column_format({1: "@"})
    driver.save()

    assert Path(tmp_path / file_name).exists()
    assert driver.col_max_length[1] >= len("value")
