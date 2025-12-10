
from parsers.row_item.row_item_formatter import get_try_to_int_or_float, get_try_to_int_or_str
import pytest


@pytest.mark.parametrize('code, assert_result', [("1", 1), ("1.0", 1), ("1.5", 1.5), ("0.5", 0.5), (None, None)])
def test_try_to_int_or_float(code, assert_result):
    assert assert_result == get_try_to_int_or_float(code)

def test_try_to_int_or_float_raise_for_str():
    with pytest.raises(ValueError):
        get_try_to_int_or_float("bar")

@pytest.mark.parametrize('code, assert_result', [("1", 1), ("1.0", 1), ("1.5", "1.5"), ('bar', 'bar')])
def test_try_to_int_or_str(code, assert_result):
    assert assert_result == get_try_to_int_or_str(code)
