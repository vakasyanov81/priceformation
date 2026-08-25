"""
tests write price for internal use
"""

import datetime
from typing import Any

from parsers.writer.fake_driver import FakeXlwtDriver
from parsers.writer.templates.tmpl.for_inner import ForInner
from parsers.writer.xls_writer import XlsWriter

from .fixtures import result_body_inner, write_data


def test_xls_write_for_inner(tmp_path: Any) -> None:
    """test write price for internal use"""

    fake_driver = FakeXlwtDriver()
    result_folder = str(tmp_path)
    XlsWriter(
        fake_driver,
        write_data,
        template=ForInner,
        result_folder=result_folder,
    ).write()
    now = datetime.datetime.now().strftime("%Y-%m-%d")

    assert fake_driver.file_name == f"price_{now}.xlsx"
    assert fake_driver.folder == result_folder
    assert fake_driver.body == result_body_inner
