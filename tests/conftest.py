"""
global fixtures
"""

import os
import sys
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../tests")))


@pytest.fixture(scope="session", autouse=True)
def default_session_fixture():
    """set flag for all tests"""
    with patch("cfg.main.__IS_UNITTEST_MODE__", True):
        yield
