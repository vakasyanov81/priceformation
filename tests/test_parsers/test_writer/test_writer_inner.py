"""
tests write price for internal use
"""

__author__ = "Kasyanov V.A."

import datetime

from src.parsers.writer.fake_driver import FakeXlwtDriver
from src.parsers.writer.templates.for_inner import ForInner
from src.parsers.writer.xls_writer import XlsWriter

from .fixtures import result_body_inner, write_data


def test_xls_write_for_inner():
    """test write price for internal use"""

    fake_driver = FakeXlwtDriver()
    XlsWriter(fake_driver, write_data, template=ForInner)
    now = datetime.datetime.now().strftime("%Y-%m-%d")

    assert fake_driver.file_name == f"price_{now}.xlsx"
    assert fake_driver.folder == "src/file_prices/result/"
    assert fake_driver.body == result_body_inner
