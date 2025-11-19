# -*- coding: utf-8 -*-
"""
tests write price for drom.ru
"""
__author__ = "Kasyanov V.A."

from unittest.mock import patch

import pytest

from src.parsers.writer.fake_driver import FakeXlwtDriver
from src.parsers.writer.xls_writer import XlsWriter
from .fixtures import FixtureTemplate, write_data


class FakeXlsWriter(XlsWriter):

    def create_folder(self):
        pass


@pytest.mark.parametrize(
    "method, call_count",
    [
        ("src.parsers.writer.fake_driver.FakeXlwtDriver.add_sheet", 1),
        ("src.parsers.writer.fake_driver.FakeXlwtDriver.write_head", 1),
        ("src.parsers.writer.fake_driver.FakeXlwtDriver.write", 3),
        ("src.parsers.writer.fake_driver.FakeXlwtDriver.save", 1),
    ],
)
def test_xls_write_call_counts(method, call_count):
    """test write price for drom.ru"""

    with patch(method) as _mock_method:
        fake_driver = FakeXlwtDriver()
        FakeXlsWriter(fake_driver, write_data, template=FixtureTemplate)

    assert _mock_method.call_count == call_count
