"""
row item field format logic
"""

from functools import lru_cache
from typing import Any, Union


def strip_into_str(field_raw: str) -> str:
    """ "_1_500_" -> "1500" """
    return field_raw.replace(" ", "")


def prepare_str_to_float(field_raw: str) -> str:
    """
    "1,500" -> "1.500"
    ">40" -> "40"
    "<40" -> "40"
    "более40" -> "40"
    """
    to_drop = ["<", ">", "более"]
    field_raw = field_raw.lower()
    for drop_item in to_drop:
        field_raw = field_raw.replace(drop_item, "")
    field_raw = field_raw.replace(",", ".")
    field_raw = field_raw.replace("руб.", "")
    return field_raw


def get_stripped(field_raw: Any, null_value: str = "") -> str:
    """get stripped value"""
    return strip_into(str(field_raw or "")) or null_value


@lru_cache()
def strip_into(field_raw: str) -> str:
    """ "abc    abc " -> "abc abc" """
    parts = field_raw.split(" ")
    return " ".join([part.strip() for part in parts if part])


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


__ALL__ = [text, code, money, floated, integer, int_or_float, boolean]
