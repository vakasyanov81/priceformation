"""Numeric / code cast helpers for row item fields."""

from functools import lru_cache
from typing import Any, Union

from parsers.row_item.row_item_strip import get_stripped, prepare_str_to_float, strip_into_str


@lru_cache()
def get_float(field_raw: Any) -> float:
    """get float value"""
    return float(prepare_str_to_float(strip_into_str(get_stripped(field_raw, null_value="0"))))


def get_integer(field_raw: Any) -> int:
    """get integer value"""
    return int(get_float(field_raw))


def get_sanitized_code(field_raw: Any) -> str:
    """
    Make correct code (article, supplier code...) after float-format xls.
    After parse xls the code (123) becomes 123.0
    """
    if isinstance(field_raw, float):
        field_raw = int(field_raw)

    return get_stripped(field_raw)


def get_try_to_int_or_str(code_value: str) -> int | str:
    """
    Try correct get_sanitized_code
    """

    def as_int_or_raise() -> int:
        code_new = get_try_to_int_or_float(code_value) or 0
        if isinstance(code_new, float):
            raise ValueError
        return int(code_new)

    try:
        return as_int_or_raise()
    except ValueError:
        return code_value


def get_try_to_int_or_float(field_raw: Union[str, float, None]) -> int | float | None:
    """
    Try Make correct str to int or float
    """
    if field_raw is None:
        return None

    numeric_raw: str | float = field_raw

    def to_int_if_whole() -> int:
        floated_value = float(numeric_raw)
        integer_value = int(floated_value)
        if floated_value - integer_value:
            raise ValueError
        return integer_value

    try:
        return to_int_if_whole()
    except ValueError:
        return float(numeric_raw)
