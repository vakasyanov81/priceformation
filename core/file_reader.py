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
    with Path(file_path).open() as _file:
        return _file.read()


__ALL__ = [read_file]
