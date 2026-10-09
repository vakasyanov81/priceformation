"""tests for terminal key decoding and reading"""

import importlib
import os
import select
import sys
import types
from collections.abc import Callable, Iterator
from typing import Any

import pytest

from run_dialog import key_codes, keys, readers


def _reader(chars: list[str]) -> Callable[[], str]:
    """Читатель, отдающий символы по очереди и падающий при перерасходе."""
    queue = list(chars)

    def _next() -> str:
        if not queue:
            raise AssertionError('прочитано больше символов, чем задано в тесте')
        return queue.pop(0)

    return _next


def _sequence(chars: str) -> Callable[[], str]:
    return _reader(list(chars))


def _never_pending() -> bool:
    """Заглушка: продолжения escape-последовательности нет."""
    return False


class _StdinDescriptor:
    """Минимальный stdin с файловым дескриптором (как у реального потока)."""

    def __init__(self, descriptor: int) -> None:
        self._descriptor = descriptor

    def fileno(self) -> int:
        return self._descriptor


@pytest.fixture
def stdin_pipe(monkeypatch: pytest.MonkeyPatch) -> Iterator[Callable[[bytes], None]]:
    """Подменить stdin реальным pipe с заранее записанными байтами.

    Пишущий конец остаётся открытым: иначе закрытый pipe читается как EOF и
    ``select`` считает, что данные есть.
    """
    opened: list[int] = []

    def _write(payload: bytes) -> None:
        read_fd, write_fd = os.pipe()
        opened.extend((read_fd, write_fd))
        os.write(write_fd, payload)
        monkeypatch.setattr(sys, 'stdin', _StdinDescriptor(read_fd))

    yield _write
    for descriptor in opened:
        os.close(descriptor)


def test_decode_char() -> None:
    """Enter, выход по q и прочие символы."""
    assert key_codes.decode_char('\r') is key_codes.Key.ENTER
    assert key_codes.decode_char('\n') is key_codes.Key.ENTER
    assert key_codes.decode_char('q') is key_codes.Key.EXIT
    assert key_codes.decode_char('Q') is key_codes.Key.EXIT
    assert key_codes.decode_char('x') is key_codes.Key.OTHER


def test_decode_unix_arrow() -> None:
    """Хвост unix-последовательности: A — вверх, B — вниз."""
    assert key_codes.decode_unix_arrow('A') is key_codes.Key.UP
    assert key_codes.decode_unix_arrow('B') is key_codes.Key.DOWN
    assert key_codes.decode_unix_arrow('C') is key_codes.Key.OTHER


def test_decode_windows_extended() -> None:
    """Второй байт windows-кода: H — вверх, P — вниз."""
    assert key_codes.decode_windows_extended('H') is key_codes.Key.UP
    assert key_codes.decode_windows_extended('P') is key_codes.Key.DOWN
    assert key_codes.decode_windows_extended('x') is key_codes.Key.OTHER


@pytest.mark.parametrize(
    ('chars', 'pending', 'expected'),
    [
        ('x', False, key_codes.Key.OTHER),
        ('\x1b', False, key_codes.Key.EXIT),
        ('\x1b[A', True, key_codes.Key.UP),
        ('\x1b[B', True, key_codes.Key.DOWN),
        ('\x1bOA', True, key_codes.Key.UP),
        ('\x1bOB', True, key_codes.Key.DOWN),
        ('\x1b[C', True, key_codes.Key.OTHER),
        ('\x1bX', True, key_codes.Key.OTHER),
    ],
)
def test_read_unix_key(chars: str, pending: bool, expected: key_codes.Key) -> None:
    """Одиночные клавиши и ESC-последовательности стрелок (CSI и SS3)."""
    assert readers.read_unix_key(_sequence(chars), lambda: pending).key is expected


@pytest.mark.parametrize(
    ('chars', 'expected'),
    [
        ('\r', key_codes.Key.ENTER),
        ('q', key_codes.Key.EXIT),
        ('\xe0H', key_codes.Key.UP),
        ('\x00P', key_codes.Key.DOWN),
        ('\xe0x', key_codes.Key.OTHER),
    ],
)
def test_read_windows_key(chars: str, expected: key_codes.Key) -> None:
    """Клавиши Windows: префикс \\x00/\\xe0 открывает расширенный код."""
    assert readers.read_windows_key(_sequence(chars)).key is expected


def test_read_unix_key_keeps_char_for_shortcut() -> None:
    """Обычный символ сохраняется для горячей клавиши."""
    press = readers.read_unix_key(_sequence('2'), _never_pending)
    assert press.key is key_codes.Key.OTHER
    assert press.char == '2'


def test_read_windows_key_keeps_char_for_shortcut() -> None:
    """Windows тоже сохраняет обычный символ для горячей клавиши."""
    press = readers.read_windows_key(_sequence('3'))
    assert press.key is key_codes.Key.OTHER
    assert press.char == '3'


@pytest.mark.parametrize('char', ['\r', 'q'])
def test_read_unix_key_clears_char_for_recognized_keys(char: str) -> None:
    """Для распознанных клавиш исходный символ не сохраняется (пусто, а не 'XXXX')."""
    press = readers.read_unix_key(_sequence(char), _never_pending)
    assert press.key is not key_codes.Key.OTHER
    assert press.char == ''


@pytest.mark.parametrize('char', ['\r', 'q'])
def test_read_windows_key_clears_char_for_recognized_keys(char: str) -> None:
    """Windows: для распознанных клавиш исходный символ тоже не сохраняется."""
    press = readers.read_windows_key(_sequence(char))
    assert press.key is not key_codes.Key.OTHER
    assert press.char == ''


def test_read_unix_key_reads_pipe(stdin_pipe: Callable[[bytes], None]) -> None:
    """Стрелка из реального fd читается целиком: байты не съедает буфер Python."""
    stdin_pipe(b'\x1b[A')
    assert readers.read_unix_key().key is key_codes.Key.UP


def test_read_unix_key_esc_alone_is_exit(stdin_pipe: Callable[[bytes], None]) -> None:
    """Одиночный ESC без продолжения — выход."""
    stdin_pipe(b'\x1b')
    assert readers.read_unix_key().key is key_codes.Key.EXIT


def test_unix_has_pending_passes_escape_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    """select вызывается с конечным таймаутом ожидания продолжения ESC."""
    recorded: dict[str, Any] = {}

    def _select(*args: Any) -> Any:
        recorded['timeout'] = args[3]
        return ([1], [], [])

    monkeypatch.setattr(select, 'select', _select)
    monkeypatch.setattr(sys, 'stdin', _StdinDescriptor(3))
    assert readers._unix_has_pending() is True  # noqa: WPS437
    assert recorded['timeout'] == readers._ESCAPE_TIMEOUT  # noqa: WPS437


def test_windows_getch(monkeypatch: pytest.MonkeyPatch) -> None:
    """Стандартный windows-читатель идёт через msvcrt.getwch."""
    fake_msvcrt = types.SimpleNamespace(getwch=_sequence('\xe0H'))
    monkeypatch.setattr(importlib, 'import_module', lambda _name: fake_msvcrt)
    assert readers.read_windows_key().key is key_codes.Key.UP


def test_read_key_dispatch(monkeypatch: pytest.MonkeyPatch) -> None:
    """Выбор платформенного читателя по os.name."""
    monkeypatch.setattr(keys, 'read_windows_key', lambda: key_codes.KeyPress(key_codes.Key.UP))
    monkeypatch.setattr(keys, 'read_unix_key', lambda: key_codes.KeyPress(key_codes.Key.DOWN))
    monkeypatch.setattr(os, 'name', 'nt')
    assert keys.read_key().key is key_codes.Key.UP
    monkeypatch.setattr(os, 'name', 'posix')
    assert keys.read_key().key is key_codes.Key.DOWN


def test_raw_terminal_restores_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    """Unix: cbreak включается, настройки восстанавливаются в finally."""
    events: list[Any] = []
    fake_termios = types.SimpleNamespace(
        TCSADRAIN=1,
        tcgetattr=lambda _fd: 'saved',
        tcsetattr=_record_restore(events),
    )
    fake_tty = types.SimpleNamespace(setcbreak=_record_cbreak(events))
    modules = {'termios': fake_termios, 'tty': fake_tty}
    monkeypatch.setattr(importlib, 'import_module', modules.__getitem__)
    monkeypatch.setattr(sys, 'stdin', _StdinDescriptor(3))
    with readers.raw_terminal():
        events.append('body')
    assert events == [('cbreak', 3), 'body', ('restore', 3, 1, 'saved')]


def test_raw_terminal_noop_on_windows(monkeypatch: pytest.MonkeyPatch) -> None:
    """Windows: режим терминала не трогаем."""
    monkeypatch.setattr(os, 'name', 'nt')
    entered = []
    with readers.raw_terminal():
        entered.append(True)
    assert entered == [True]


def _record_cbreak(events: list[Any]) -> Callable[[int], None]:
    def _cbreak(descriptor: int) -> None:
        events.append(('cbreak', descriptor))

    return _cbreak


def _record_restore(events: list[Any]) -> Callable[[int, int, str], None]:
    def _restore(descriptor: int, when: int, saved: str) -> None:
        events.append(('restore', descriptor, when, saved))

    return _restore
