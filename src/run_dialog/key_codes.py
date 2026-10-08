"""Коды клавиш: распознанные нажатия и декодеры символов."""

import dataclasses
from enum import Enum, auto


class Key(Enum):
    """Распознанное нажатие клавиши."""

    UP = auto()
    DOWN = auto()
    ENTER = auto()
    EXIT = auto()
    OTHER = auto()


@dataclasses.dataclass(frozen=True)
class KeyPress:
    """Нажатие: распознанная клавиша и исходный символ для горячих клавиш."""

    key: Key
    char: str = ''


def decode_char(char: str) -> Key:
    """Одиночный символ: Enter, выход или прочее."""
    if char in ('\r', '\n'):
        return Key.ENTER
    if char.lower() == 'q':
        return Key.EXIT
    return Key.OTHER


def decode_unix_arrow(sequence: str) -> Key:
    """Хвост escape-последовательности стрелки в Unix-терминале."""
    if sequence == 'A':
        return Key.UP
    if sequence == 'B':
        return Key.DOWN
    return Key.OTHER


def decode_windows_extended(code: str) -> Key:
    """Второй символ расширенного кода клавиши в Windows-терминале."""
    if code == 'H':
        return Key.UP
    if code == 'P':
        return Key.DOWN
    return Key.OTHER
