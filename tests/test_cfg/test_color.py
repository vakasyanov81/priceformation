"""tests for color scheme constants"""

from cfg.color import Colors

_ANSI_PREFIX = "\033["


def test_header_and_ok_colors():
    """HEADER и OK-* используют ANSI-префикс"""
    assert Colors.HEADER.startswith(_ANSI_PREFIX)
    assert Colors.OK_BLUE.startswith(_ANSI_PREFIX)
    assert Colors.OK_CYAN.startswith(_ANSI_PREFIX)
    assert Colors.OK_GREEN.startswith(_ANSI_PREFIX)


def test_warning_fail_and_style_colors():
    """WARNING/FAIL и стиль форматирования"""
    assert Colors.WARNING.startswith(_ANSI_PREFIX)
    assert Colors.FAIL.startswith(_ANSI_PREFIX)
    assert Colors.END_COLOR == "\033[0m"
    assert Colors.BOLD == "\033[1m"
    assert Colors.UNDERLINE == "\033[4m"
