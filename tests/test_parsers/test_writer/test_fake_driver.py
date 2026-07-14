"""tests for FakeXlwtDriver"""

from parsers.writer.fake_driver import FakeXlwtDriver

_FOLDER = "folder/"
_FILE_NAME = "file.xls"
_SHEET = "Sheet1"
_WIDTH = 100


def test_fake_driver_init_and_sheet():
    """init workbook и лист"""
    driver = FakeXlwtDriver()
    driver.init_workbook(_FOLDER, _FILE_NAME)
    driver.add_sheet(_SHEET)
    driver.set_width(0, _WIDTH)
    assert driver.folder == _FOLDER
    assert driver.file_name == _FILE_NAME
    assert driver.sheet_name == _SHEET
    assert driver.width[0] == _WIDTH
    assert driver.get_folder() == _FOLDER


def test_fake_driver_write_body():
    """запись шапки и тела"""
    driver = FakeXlwtDriver()
    driver.write_head(["a", "b"])
    driver.write(1, 0, "val")
    driver.set_column_format({0: "@"})
    driver.save()
    assert driver.head == ["a", "b"]
    assert driver.body["cell(1,0)"] == "val"


def test_fake_driver_repr():
    """__repr__ отражает состояние драйвера"""
    driver = FakeXlwtDriver()
    driver.init_workbook("f/", "n.xls")
    driver.add_sheet("S")
    text = repr(driver)
    assert "FakeXlwtDriver" in text
    assert "n.xls" in text
    assert "S" in text
