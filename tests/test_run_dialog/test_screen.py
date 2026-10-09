"""tests for terminal screen rendering and frame height tracking"""

import pytest

from run_dialog import screen
from run_dialog.rows import MenuRow

_ROWS = [MenuRow('one', shortcut='1'), MenuRow('two', shortcut='2')]


def test_draw_returns_frame_height() -> None:
    """Высота кадра = заголовок плюс строки меню."""
    assert screen.draw(_ROWS, 0, previous=0) == len(_ROWS) + 1


def test_draw_moves_up_by_previous_height(capsys: pytest.CaptureFixture[str]) -> None:
    """Перерисовка отъезжает вверх ровно на высоту прошлого кадра."""
    screen.draw(_ROWS, 1, previous=5)
    out = capsys.readouterr().out
    assert out.startswith('\x1b[5F')
    assert '\x1b[J' in out


def test_draw_highlights_active(capsys: pytest.CaptureFixture[str]) -> None:
    """Активная строка подсвечивается."""
    screen.draw(_ROWS, 1, previous=0)
    assert '\x1b[7mtwo\x1b[0m' in capsys.readouterr().out


def test_settle_keeps_only_selected(capsys: pytest.CaptureFixture[str]) -> None:
    """settle стирает кадр и оставляет только выбранную строку."""
    screen.settle(_ROWS, 1, previous=3)
    out = capsys.readouterr().out
    assert out.startswith('\x1b[3F')
    assert 'two' in out
    assert 'one' not in out


def test_rewrite_writes_exact_control_sequence(capsys: pytest.CaptureFixture[str]) -> None:
    """Кадр — стирание хвоста, строки через \\n и завершающий \\n, без посторонних символов."""
    screen.draw(_ROWS, 0, previous=0)
    expected = '\x1b[J' + '\n'.join(screen.render(_ROWS, 0)) + '\n'
    assert capsys.readouterr().out == expected
