"""
tests write duplicates report
"""

import datetime
from typing import Any

from parsers.writer.fake_driver import FakeXlwtDriver
from parsers.writer.templates.tmpl.for_doubles import ForDoubles
from parsers.writer.xls_writer import XlsWriter

from .fixtures import result_body_inner, write_data

_GROUP_COL = 14
_IS_DOUBLE_COL = 15
_CANDIDATE_COL = 16
_DISPUTED_COL = 17
_DOUBLE_HEAD = ["Группа по параметрам", "Дубль", "Главный дубль", "Спорная"]


def test_xls_write_for_doubles(tmp_path: Any) -> None:
    """отчёт о дублях: колонки внутреннего прайса плюс признаки дубля"""
    row = {
        **write_data[0],
        "group_by_params": 1,
        "is_double": True,
        "double_candidate": False,
    }
    fake_driver = FakeXlwtDriver()
    result_folder = str(tmp_path)
    XlsWriter(
        fake_driver,
        [row],
        template=ForDoubles,
        result_folder=result_folder,
    ).write()
    now = datetime.datetime.now().strftime("%Y-%m-%d")

    assert fake_driver.file_name == f"doubles_{now}.xlsx"
    assert fake_driver.folder == result_folder
    assert fake_driver.head[-4:] == _DOUBLE_HEAD
    assert fake_driver.body == {
        **result_body_inner,
        f"cell(1,{_GROUP_COL})": 1,
        f"cell(1,{_IS_DOUBLE_COL})": True,
    }
    assert f"cell(1,{_CANDIDATE_COL})" not in fake_driver.body
    assert f"cell(1,{_DISPUTED_COL})" not in fake_driver.body


def test_xls_write_for_doubles_disputed(tmp_path: Any) -> None:
    """спорная группа дублей — колонка Спорная заполнена"""
    row = {
        **write_data[0],
        "group_by_params": 1,
        "is_double": True,
        "disputed": "шип",
    }
    fake_driver = FakeXlwtDriver()
    XlsWriter(
        fake_driver,
        [row],
        template=ForDoubles,
        result_folder=str(tmp_path),
    ).write()

    assert fake_driver.head[-4:] == _DOUBLE_HEAD
    assert fake_driver.body[f"cell(1,{_DISPUTED_COL})"] == "шип"
