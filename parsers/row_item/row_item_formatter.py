# -*- coding: utf-8 -*-
"""
row item field format logic
"""
__author__ = "Kasyanov V.A."

from functools import lru_cache
from typing import Optional, Union


def strip_into_str(value: str) -> str:
    """  "_1_500_" -> "1500"   """
    return value.replace(" ", "")


def prepare_str_to_float(value: str) -> str:
    """
    "1,500" -> "1.500"
    ">40" -> "40"
    "<40" -> "40"
    "более40" -> "40"
    """
    _to_drop = ["<", ">", "более"]
    for drop_item in _to_drop:
        value = value.replace(drop_item, "")
    return value.replace(",", ".")


def get_stripped(value, null_value="") -> str:
    """ get stripped value """
    return strip_into(str(value or "")) or null_value


@lru_cache()
def strip_into(value: str):
    """ "abc    abc " -> "abc abc"  """
    _val = value.split(" ")
    _val = " ".join([__val.strip() for __val in _val if __val])
    return _val


@lru_cache()
def get_float(value) -> float:
    """ get float value """
    return float(
        prepare_str_to_float(
            strip_into_str(
                get_stripped(value, null_value="0")
            )
        )
    )


def get_integer(value) -> int:
    """ get integer value """
    return int(get_float(value))


def get_sanitized_code(value):
    """
    Make correct code (article, supplier code...) after float-format xls.
    After parse xls the code (123) becomes 123.0
    """
    if isinstance(value, float):
        value = int(value)

    return get_stripped(value)


def get_try_to_int(value: Union[str, float]) -> Optional[Union[int, float]]:
    """
    Try Make correct str to int
    """

    if value is None:
        return value

    try:
        value = float(value)
        value_int = int(value)
        if value - value_int:
            raise ValueError
        return value_int
    except ValueError:
        return float(value)


def call_wrapper(_self, decorated_func, format_func_getter, *args):
    """ make call wrapper for property and property-setter """
    if args:
        return decorated_func(_self, format_func_getter(args[0]))
    return format_func_getter(decorated_func(_self))


def text(_func):
    """ text decorator """
    def wrap(_self, *args):
        """ wrapper """
        return call_wrapper(_self, _func, get_stripped, *args)
    return wrap


def money(_func):
    """ money decorator """
    return floated(_func)


def floated(_func):
    """ float-value decorator """

    def wrap(_self, *args):
        """ wrapper """
        return call_wrapper(_self, _func, get_float, *args)
    return wrap


def integer(_func):
    """ integer decorator """

    def wrap(_self, *args):
        """ wrapper """
        return call_wrapper(_self, _func, get_integer, *args)
    return wrap


def code(_func):
    """ prepare code """

    def wrap(_self, *args):
        """ wrapper """
        return call_wrapper(_self, _func, get_sanitized_code, *args)

    return wrap


def int_or_float(_func):
    """ try cast to int """

    def wrap(_self, *args):
        """ wrapper """
        return call_wrapper(_self, _func, get_try_to_int, *args)

    return wrap


__ALL__ = [
    text,
    code,
    money,
    floated,
    integer,
    int_or_float
]
