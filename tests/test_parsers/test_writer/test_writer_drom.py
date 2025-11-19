# -*- coding: utf-8 -*-
"""
tests write price for drom.ru
"""
__author__ = "Kasyanov V.A."

import datetime
import os

from src.parsers.writer.fake_driver import FakeXlwtDriver
from src.parsers.writer.templates.tmpl.for_drom import ForDrom
from .fixtures import result_body_drom, write_data
from .test_writer import FakeXlsWriter


def test_xls_write_for_drom():
    """test write price for drom.ru"""

    fake_driver = FakeXlwtDriver()
    FakeXlsWriter(fake_driver, write_data, template=ForDrom)
    now = datetime.datetime.now().strftime("%Y-%m-%d")

    assert fake_driver.file_name == f"price_drom_{now}.xlsx"
    assert fake_driver.folder == f"file_prices{os.sep}result{os.sep}"
    assert fake_driver.body == result_body_drom
