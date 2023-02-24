# -*- coding: utf-8 -*-
"""
tests write price for drom.ru
"""
__author__ = "Kasyanov V.A."

import datetime

from parsers.writer.fake_driver import FakeXlwtDriver
from parsers.writer.templates.for_drom import ForDrom
from parsers.writer.xls_writer import XlsWriter

from .fixtures import result_body_drom, write_data


def test_xls_write_for_drom():
    """test write price for drom.ru"""

    fake_driver = FakeXlwtDriver()
    XlsWriter(fake_driver, write_data, template=ForDrom)
    now = datetime.datetime.now().strftime("%Y-%m-%d")

    assert fake_driver.file_name == f"price_drom_{now}.xlsx"
    assert fake_driver.folder == "file_prices/result/"
    assert fake_driver.body == result_body_drom
