"""
tests write duplicates report
"""

import datetime
import os
from unittest.mock import MagicMock, patch

from parsers.writer.fake_driver import FakeXlwtDriver
from parsers.writer.templates.tmpl.for_doubles import ForDoubles
from parsers.writer.xls_writer import XlsWriter

from .fixtures import result_body_inner, write_data

_GROUP_COL = 14
_IS_DOUBLE_COL = 15
_CANDIDATE_COL = 16


@patch("parsers.writer.xls_writer.create_result_folder", MagicMock(return_value=None))
def test_xls_write_for_doubles() -> None:
    """отчёт о дублях: колонки внутреннего прайса плюс признаки дубля"""
    row = {
        **write_data[0],
        "group_by_params": 1,
        "is_double": True,
        "double_candidate": False,
    }
    fake_driver = FakeXlwtDriver()
    XlsWriter(fake_driver, [row], template=ForDoubles)
    now = datetime.datetime.now().strftime("%Y-%m-%d")

    assert fake_driver.file_name == f"doubles_{now}.xlsx"
    assert f"file_prices{os.sep}result" in (fake_driver.folder or "")
    assert fake_driver.head[-3:] == ["Группа по параметрам", "Дубль", "Главный дубль"]
    assert fake_driver.body == {
        **result_body_inner,
        f"cell(1,{_GROUP_COL})": 1,
        f"cell(1,{_IS_DOUBLE_COL})": True,
    }
    assert f"cell(1,{_CANDIDATE_COL})" not in fake_driver.body
