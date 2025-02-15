# -*- coding: utf-8 -*-
"""
read file logic
"""
__author__ = "Kasyanov V.A."

from pathlib import Path

from .wrappers import logging


@logging(label="...reading file...")
def read_file(file_path):
    """read file"""
    with Path(file_path).open(encoding="UTF-8") as _file:
        return _file.read()


def try_read_file(file_path):
    """try read file"""
    try:
        return read_file(file_path)
    except FileNotFoundError:
        return ""


__ALL__ = [read_file]
