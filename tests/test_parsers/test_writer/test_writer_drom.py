"""
tests write price for drom.ru
"""

import datetime
from typing import Any

from parsers.writer.fake_driver import FakeXlwtDriver
from parsers.writer.templates.tmpl.for_drom import ForDrom
from parsers.writer.xls_writer import XlsWriter

from .fixtures import result_body_drom, write_data


def test_xls_write_for_drom(tmp_path: Any) -> None:
    """test write price for drom.ru"""

    fake_driver = FakeXlwtDriver()
    result_folder = str(tmp_path)
    XlsWriter(
        fake_driver,
        write_data,
        template=ForDrom,
        result_folder=result_folder,
    ).write()
    now = datetime.datetime.now().strftime("%Y-%m-%d")

    assert fake_driver.file_name == f"price_drom_{now}.xlsx"
    assert fake_driver.folder == result_folder
    assert fake_driver.body == result_body_drom
