"""Отрисовка меню в терминале: строки, подсветка активной, перерисовка поверх."""

import sys

from cfg.color import Colors
from run_dialog.rows import MenuRow

_HEADER = 'Выберите действие (стрелки ↑/↓, Enter — выбрать, q — выход):'


def render(rows: list[MenuRow], active: int) -> list[str]:
    """Строки вывода: заголовок и меню, активная строка подсвечена."""
    lines = [_HEADER]
    for index, row in enumerate(rows):
        text = row.text
        if index == active:
            text = f'{Colors.REVERSE}{text}{Colors.END_COLOR}'
        lines.append(text)
    return lines


def draw(rows: list[MenuRow], active: int, *, previous: int) -> int:
    """Нарисовать меню поверх прошлого кадра; вернуть высоту нового кадра.

    ``previous`` — сколько строк занимал прошлый кадр: курсор поднимается ровно
    на них, поэтому при сокращении списка старые строки не остаются висеть.
    """
    lines = render(rows, active)
    _rewrite(lines, previous)
    return len(lines)


def settle(rows: list[MenuRow], active: int, *, previous: int) -> None:
    """Стереть кадр и оставить только выбранную строку."""
    _rewrite([rows[active].text], previous)


def _rewrite(lines: list[str], previous: int) -> None:
    """Поднять курсор на прошлый кадр, очистить низ и напечатать новые строки."""
    if previous:
        sys.stdout.write(f'\x1b[{previous}F')
    sys.stdout.write('\x1b[J')
    sys.stdout.write('\n'.join(lines))
    sys.stdout.write('\n')
    sys.stdout.flush()
