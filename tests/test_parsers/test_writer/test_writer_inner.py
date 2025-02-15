"""
tests write price for internal use
"""

__author__ = "Kasyanov V.A."

import datetime
import os

from src.parsers.writer.fake_driver import FakeXlwtDriver
from src.parsers.writer.templates.for_inner import ForInner
from .fixtures import result_body_inner, write_data
from .test_writer import TestXlsWriter


def test_xls_write_for_inner():
    """test write price for internal use"""

    fake_driver = FakeXlwtDriver()
    TestXlsWriter(fake_driver, write_data, template=ForInner)
    now = datetime.datetime.now().strftime("%Y-%m-%d")

    assert fake_driver.file_name == f"price_{now}.xlsx"
    assert fake_driver.folder == f"file_prices{os.sep}result{os.sep}"
    assert fake_driver.body == result_body_inner
