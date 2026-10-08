"""Выбор платформенного читателя клавиш."""

import os

from run_dialog.key_codes import KeyPress
from run_dialog.readers import read_unix_key, read_windows_key


def read_key() -> KeyPress:
    """Прочитать одно нажатие из терминала."""
    if os.name == 'nt':
        return read_windows_key()
    return read_unix_key()
