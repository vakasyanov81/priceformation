"""
read file logic
"""

import json
from pathlib import Path
from typing import Any

from domain.exceptions import ConfigValidationError
from infrastructure.logging.wrappers import logging


@logging(label='...reading file...')
def read_file(file_path: str) -> str:
    """read file"""
    with Path(file_path).open(encoding='UTF-8') as text_file:
        return text_file.read()


def read_json_file(file_path: str) -> Any:
    """Прочитать JSON-файл; нечитаемый JSON — `ConfigValidationError` с именем файла."""
    try:
        return json.loads(read_file(file_path))
    except json.JSONDecodeError as exc:
        raise ConfigValidationError(f'{Path(file_path).name}: не удалось разобрать JSON ({exc})') from exc


def try_read_file(file_path: str) -> str:
    """try read file"""
    try:
        return read_file(file_path)
    except FileNotFoundError:
        return ''


__ALL__ = [read_file, read_json_file]
