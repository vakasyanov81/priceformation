# -*- coding: utf-8 -*-
"""
read file logic
"""
__author__ = "Kasyanov V.A."

from .wrappers import logging


@logging(label="...reading file...")
def read_file(file_path, encoding="utf-8"):
    """ read file """
    with open(file_path, "rb") as _file:
        read_data = _file.read().decode(encoding=encoding)

    return read_data


__ALL__ = [read_file]
