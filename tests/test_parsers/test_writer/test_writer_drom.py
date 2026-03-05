"""
tests write price for drom.ru
"""

import datetime
import os
from unittest.mock import patch, MagicMock

from parsers.writer.fake_driver import FakeXlwtDriver
from parsers.writer.templates.tmpl.for_drom import ForDrom
from .fixtures import result_body_drom, write_data
from .test_writer import XlsWriter


@patch("parsers.writer.xls_writer.create_result_folder", MagicMock(return_value=None))
def test_xls_write_for_drom():
    """test write price for drom.ru"""

    fake_driver = FakeXlwtDriver()
    XlsWriter(fake_driver, write_data, template=ForDrom)
    now = datetime.datetime.now().strftime("%Y-%m-%d")

    assert fake_driver.file_name == f"price_drom_{now}.xlsx"
    assert f"file_prices{os.sep}result" in fake_driver.get_folder()
    assert fake_driver.body == result_body_drom
