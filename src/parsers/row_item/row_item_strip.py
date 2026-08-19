"""String strip / normalize helpers for row item fields."""

from functools import lru_cache
from typing import Any


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
    return field_raw.replace(",", ".").replace("руб.", "")


def get_stripped(field_raw: Any, null_value: str = "") -> str:
    """get stripped value"""
    return strip_into(str(field_raw or "")) or null_value


@lru_cache
def strip_into(field_raw: str) -> str:
    """ "abc    abc " -> "abc abc" """
    parts = field_raw.split(" ")
    return " ".join([part.strip() for part in parts if part])
