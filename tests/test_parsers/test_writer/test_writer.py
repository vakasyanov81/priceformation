# -*- coding: utf-8 -*-
"""
tests write price for drom.ru
"""
__author__ = "Kasyanov V.A."

from unittest.mock import patch
import pytest
from parsers.writer.xls_writer import XlsWriter
from parsers.writer.fake_driver import FakeXlwtDriver
from .fixtures import FixtureTemplate
from .fixtures import write_data


@pytest.mark.parametrize(
    "method, call_count", [
        ("parsers.writer.fake_driver.FakeXlwtDriver.add_sheet", 1),
        ("parsers.writer.fake_driver.FakeXlwtDriver.write_head", 1),
        ("parsers.writer.fake_driver.FakeXlwtDriver.write", 3),
        ("parsers.writer.fake_driver.FakeXlwtDriver.save", 1)
    ]
)
def test_xls_write_call_counts(method, call_count):
    """ test write price for drom.ru  """

    with patch(method) as _mock_method:
        fake_driver = FakeXlwtDriver()
        XlsWriter(fake_driver, write_data, template=FixtureTemplate)

    assert _mock_method.call_count == call_count
