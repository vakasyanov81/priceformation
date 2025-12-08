"""
read file logic
"""

from pathlib import Path

from .wrappers import logging


@logging(label="...reading file...")
def read_file(file_path: str) -> str:
    """read file"""
    with Path(file_path).open(encoding="UTF-8") as _file:
        return _file.read()


def try_read_file(file_path: str) -> str:
    """try read file"""
    try:
        return read_file(file_path)
    except FileNotFoundError:
        return ""


__ALL__ = [read_file]
