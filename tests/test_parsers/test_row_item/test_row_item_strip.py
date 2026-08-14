"""tests for row item strip / code sanitizers."""

import pytest

from parsers.row_item.row_item_casts import get_sanitized_code
from parsers.row_item.row_item_strip import get_stripped, prepare_str_to_float, strip_into_str

_XLS_FLOAT_CODE = 123.0
_SANITIZED_CODE = "123"


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("<40", "40"),
        (">40", "40"),
        ("БОЛЕЕ40", "40"),
        ("1,500", "1.500"),
        ("100руб.", "100"),
    ],
)
def test_prepare_str_to_float(raw: str, expected: str) -> None:
    assert prepare_str_to_float(raw) == expected


def test_strip_into_str_drops_spaces() -> None:
    assert strip_into_str("1 500") == "1500"


def test_get_stripped_none() -> None:
    assert get_stripped(None) == ""


def test_get_sanitized_code_from_xls_float() -> None:
    assert get_sanitized_code(_XLS_FLOAT_CODE) == _SANITIZED_CODE


def test_get_sanitized_code_keeps_string() -> None:
    assert get_sanitized_code("ABC") == "ABC"
