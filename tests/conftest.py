# -*- coding: utf-8 -*-
"""
global fixtures
"""
__author__ = "Kasyanov V.A."

from unittest.mock import patch

import pytest

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../tests')))


def pytest_make_parametrize_id(val):
    """for unicode representation"""
    return repr(val)


@pytest.fixture(scope="session", autouse=True)
def default_session_fixture():
    """set flag for all tests"""
    with patch("cfg.main.__IS_UNITTEST_MODE__", True):
        yield
