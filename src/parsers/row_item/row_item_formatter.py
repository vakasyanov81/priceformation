"""
row item field format logic
"""

from typing import Any

from parsers.row_item.row_item_casts import get_float, get_integer, get_sanitized_code, get_try_to_int_or_float
from parsers.row_item.row_item_strip import get_stripped


def text(field_raw: Any) -> str:
    """text decorator"""
    return get_stripped(field_raw)


def money(field_raw: Any) -> float:
    """money decorator"""
    return floated(field_raw)


def floated(field_raw: Any) -> float:
    """float-value decorator"""
    return get_float(field_raw)


def integer(field_raw: Any) -> int:
    """integer decorator"""
    return get_integer(field_raw)


def code(field_raw: Any) -> str:
    """prepare code"""
    return get_sanitized_code(field_raw)


def int_or_float(field_raw: Any) -> int | float | None:
    """try cast to int"""
    return get_try_to_int_or_float(field_raw)


def boolean(field_raw: Any) -> bool:
    """try cast to boolean"""
    return bool(field_raw)
