"""tests for print_log output"""

import logging
from collections.abc import Iterator
from contextlib import redirect_stdout
from io import StringIO

import pytest

from core.log_message import print_log, set_print_quiet, set_print_stream


@pytest.fixture(autouse=True)
def _reset_print_quiet() -> Iterator[None]:
    """JSON-quiet не должен протекать между тестами."""
    set_print_quiet(False)
    yield
    set_print_quiet(False)


def test_print_log_info_level() -> None:
    """info level prints bare message"""
    out = StringIO()
    with redirect_stdout(out):
        print_log("message")

    assert out.getvalue() == "message\n"


def test_print_log_error_level() -> None:
    """error level prints prefixed message"""
    out = StringIO()
    with redirect_stdout(out):
        print_log("message", level=logging.ERROR)

    assert out.getvalue() == "[ERROR]: message\n"


def test_print_log_custom_stream() -> None:
    """set_print_stream направляет вывод в указанный поток."""
    stream = StringIO()
    set_print_stream(stream)
    print_log("to-stderr")
    set_print_stream(None)
    assert stream.getvalue() == "to-stderr\n"


def test_print_log_quiet() -> None:
    """quiet глушит print_log, stdout остаётся пустым."""
    out = StringIO()
    set_print_quiet(True)
    with redirect_stdout(out):
        print_log("hidden")
    set_print_quiet(False)
    assert out.getvalue() == ""
