"""Назначение шины в названии: слова оси, шипов, особенностей (`об/л`, `вед.ось`, `(карьер)`)."""

from __future__ import annotations

import re

from parsers.strategies._tire_size_parts import DOT

_USAGE_WORDS = frozenset(
    (
        'об/л',
        'об/лента',
        'шипы',
        'шип',
        'шип.',
        'б/к',
        '(карьер)',
        '(шашка)',
        '(волна)',
        '(клюшка)',
        'с',
        'трал',
        'шашка',
        'волна',
        'клюшка',
        'спецшина',
        'спецпокрышка',
        'сельхозшина',
        'сельхозпокрышка',
        'цельнолит',
        'змейка',
        'стройка',
        'кам',
        'зимняя',
    ),
)
# Начала токенов назначения: оси (`вед.ось`, `вед`, `руль/прицеп`, `приц.`, канонические `Универсальная`),
# индекс (`инд.102`), карьерный протектор (`карьер`, `карьерка/вед`).
_USAGE_PREFIXES = ('инд.', 'ось', 'вед', 'рул', 'унив', 'приц', 'карьер')
# Описание в скобках после модели строчными русскими словами: `(экскаватор)`, `(прерывистая волна)`.
_USAGE_PAREN = re.compile(r'\([а-яё][а-яё\s.,-]*\)')
# Корень слова назначения → значение оси: `вед.ось`, `унив.ось`, `рулевая`, `приц.`, `руль/прицеп`.
_AXES = (
    ('вед', 'ведущая'),
    ('рул', 'рулевая'),
    ('унив', 'универсальная'),
    ('приц', 'прицепная'),
    ('карьер', 'карьерная'),
)
_SPIKE_TOKENS = frozenset(('шип', 'шипы'))
_SPIKE_YES = 'Да'


def is_usage(token: str) -> bool:
    """Токен назначения/особенности: об/л, оси, шипы, инд., карьер и т.п."""
    lower = token.lower()
    return lower in _USAGE_WORDS or lower.startswith(_USAGE_PREFIXES)


def axis(usage: tuple[str, ...]) -> str:
    """Ось из слов назначения; при нескольких (``рулевая/трал``) — по первому слову."""
    for token in usage:
        lower = token.lower()
        for root, root_axis in _AXES:
            if lower.startswith(root):
                return root_axis
    return ''


def spike(usage: tuple[str, ...]) -> str:
    """``Да``, если в назначении есть шипы (``шип``, ``шипы``, ``шип.``); иначе пусто."""
    words = (token.lower().strip(DOT) for token in usage)
    return _SPIKE_YES if _SPIKE_TOKENS.intersection(words) else ''


def trailing_paren_start(tokens: list[str]) -> int:
    """Начало описания в скобках в конце токенов (`(прерывистая волна)`, `(цельнолитая)`); без него — длина списка.

    Скобки с цифрами или латиницей (`(У-2)`, `(HK-245)`, `(snow)`) — часть названия модели, не описание.
    """
    if not tokens or not tokens[-1].endswith(')'):
        return len(tokens)
    for index in range(len(tokens) - 1, 0, -1):
        if tokens[index].startswith('('):
            described = _USAGE_PAREN.fullmatch(' '.join(tokens[index:]))
            return index if described else len(tokens)
        if ')' in tokens[index - 1]:
            break
    return len(tokens)
