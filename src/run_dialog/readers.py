"""Низкоуровневое чтение клавиш терминала и режим cbreak.

Платформенные различия скрыты за ``read_unix_key``/``read_windows_key``.
Низкоуровневые читатели передаются параметрами, поэтому обе ветки проверяются
тестами на любой ОС.
"""

import importlib
import os
import select
import sys
from collections.abc import Callable, Iterator
from contextlib import contextmanager

from run_dialog.key_codes import Key, KeyPress, decode_char, decode_unix_arrow, decode_windows_extended

_ESCAPE_TIMEOUT = 0.05


def _unix_read_char() -> str:
    """Прочитать один байт из stdin напрямую через fd, минуя буфер Python."""
    return os.read(sys.stdin.fileno(), 1).decode('utf-8', 'ignore')


def _unix_has_pending() -> bool:
    """Есть ли в stdin непрочитанные байты (продолжение escape-последовательности)."""
    descriptor = sys.stdin.fileno()
    ready = select.select([descriptor], [], [], _ESCAPE_TIMEOUT)[0]
    return bool(ready)


def _windows_getch() -> str:
    """Прочитать один символ через msvcrt."""
    getwch: Callable[[], str] = importlib.import_module('msvcrt').getwch
    return getwch()


def read_unix_key(
    read_char: Callable[[], str] = _unix_read_char,
    has_pending: Callable[[], bool] = _unix_has_pending,
) -> KeyPress:
    """Одно нажатие в Unix: стрелки приходят как ESC [ A/B или ESC O A/B."""
    char = read_char()
    if char == '\x1b':
        if not has_pending():
            return KeyPress(Key.EXIT)
        if read_char() not in ('[', 'O'):
            return KeyPress(Key.OTHER)
        return KeyPress(decode_unix_arrow(read_char()))
    key = decode_char(char)
    return KeyPress(key, char if key is Key.OTHER else '')


def read_windows_key(getch: Callable[[], str] = _windows_getch) -> KeyPress:
    """Одно нажатие в Windows: стрелки идут после нулевого/расширенного префикса."""
    char = getch()
    if char in ('\x00', '\xe0'):
        return KeyPress(decode_windows_extended(getch()))
    key = decode_char(char)
    return KeyPress(key, char if key is Key.OTHER else '')


@contextmanager
def raw_terminal() -> Iterator[None]:
    """Перевести stdin в cbreak на Unix; на Windows ничего не делать."""
    if os.name == 'nt':
        yield
        return
    termios = importlib.import_module('termios')
    tty = importlib.import_module('tty')
    descriptor = sys.stdin.fileno()
    saved = termios.tcgetattr(descriptor)
    tty.setcbreak(descriptor)
    try:
        yield
    finally:
        termios.tcsetattr(descriptor, termios.TCSADRAIN, saved)
