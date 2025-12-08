from io import StringIO
from contextlib import redirect_stdout
import logging
from core.log_message import print_log


def test_print_log_info_level():
    out = StringIO()
    with redirect_stdout(out):
        print_log('message')

    assert out.getvalue() == 'message\n'


def test_print_log_error_level():
    out = StringIO()
    with redirect_stdout(out):
        print_log('message', level=logging.ERROR)

    assert out.getvalue() == '[ERROR]: message\n'
