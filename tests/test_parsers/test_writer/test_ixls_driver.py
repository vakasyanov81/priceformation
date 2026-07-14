"""tests for IXlsDriver abstract interface"""

import pytest

from parsers.writer.ixls_driver import IXlsDriver


def test_add_sheet_raises():
    with pytest.raises(NotImplementedError):
        IXlsDriver().add_sheet("s")


def test_write_head_raises():
    with pytest.raises(NotImplementedError):
        IXlsDriver().write_head([])


def test_set_column_format_raises():
    with pytest.raises(NotImplementedError):
        IXlsDriver().set_column_format({})


def test_write_raises():
    with pytest.raises(NotImplementedError):
        IXlsDriver().write(0, 0, None)


def test_save_raises():
    with pytest.raises(NotImplementedError):
        IXlsDriver().save()


def test_init_workbook_raises():
    with pytest.raises(NotImplementedError):
        IXlsDriver().init_workbook("f", "n")
