"""
tests write price for internal use
"""

import datetime
import os
from unittest.mock import patch, MagicMock

from parsers.writer.fake_driver import FakeXlwtDriver
from parsers.writer.templates.tmpl.for_inner import ForInner
from .fixtures import result_body_inner, write_data
from .test_writer import XlsWriter


@patch("parsers.writer.xls_writer.create_result_folder", MagicMock(return_value=None))
def test_xls_write_for_inner():
    """test write price for internal use"""

    fake_driver = FakeXlwtDriver()
    XlsWriter(fake_driver, write_data, template=ForInner)
    now = datetime.datetime.now().strftime("%Y-%m-%d")

    assert fake_driver.file_name == f"price_{now}.xlsx"
    assert f"file_prices{os.sep}result" in fake_driver.get_folder()
    assert fake_driver.body == result_body_inner
