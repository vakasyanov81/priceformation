"""Подсветка markdown-справки для терминала: заголовки, код, инлайн-разметка."""

import re

from cfg.color import Colors

_HEADING = re.compile(r'^(#{1,6})\s+(.*)$')
_FENCE = re.compile(r'^\s*```')
_BOLD = re.compile(r'\*\*(.+?)\*\*')
_CODE = re.compile(r'`([^`]+)`')
_LINK = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

_HEADING_COLORS = {
    1: Colors.HEADER,
    2: Colors.OK_BLUE,
    3: Colors.OK_CYAN,
}
_HEADING_FALLBACK = Colors.OK_GREEN


def colorize_markdown(text: str) -> str:
    """Раскрасить markdown ANSI-кодами: заголовки, блоки кода, жирный, ссылки."""
    lines: list[str] = []
    in_code = False
    for line in text.splitlines():
        if _FENCE.match(line):
            in_code = not in_code
            lines.append(_paint(Colors.WARNING, line))
        elif in_code:
            lines.append(_paint(Colors.OK_GREEN, line))
        else:
            lines.append(_colorize_line(line))
    return '\n'.join([*lines, ''])


def _colorize_line(line: str) -> str:
    """Заголовок — цветом по уровню, иначе инлайн-разметка."""
    heading = _HEADING.match(line)
    if heading is not None:
        color = _HEADING_COLORS.get(len(heading.group(1)), _HEADING_FALLBACK)
        return f'{color}{Colors.BOLD}{heading.group(2)}{Colors.END_COLOR}'
    return _inline(line)


def _inline(line: str) -> str:
    """Ссылки, жирный и инлайн-код внутри строки.

    Ссылки окрашиваются первыми: их ANSI-обрамление содержит квадратную скобку,
    из-за чего шаблон ссылки иначе захватывал бы уже окрашенный текст.
    """
    line = _LINK.sub(_link, line)
    line = _BOLD.sub(rf'{Colors.BOLD}\1{Colors.END_COLOR}', line)
    return _CODE.sub(rf'{Colors.OK_CYAN}\1{Colors.END_COLOR}', line)


def _link(match: re.Match[str]) -> str:
    """Подпись ссылки; внутренние якоря (`#...`) — без самого адреса."""
    label = match.group(1)
    target = match.group(2)
    if target.startswith('#'):
        return f'{Colors.UNDERLINE}{label}{Colors.END_COLOR}'
    return f'{label} ({Colors.UNDERLINE}{target}{Colors.END_COLOR})'


def _paint(color: str, line: str) -> str:
    """Окрасить строку целиком, вернув цвет к обычному."""
    return f'{color}{line}{Colors.END_COLOR}'
