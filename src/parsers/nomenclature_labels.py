"""Каноническое написание токенов названия шины: слойность, камерность, ось."""

import re

_DIGITS = re.compile(r'\d+')
_CAMERA_TL = 'TL'
_CAMERA_CODE = re.compile(r'TT|TL|TTF|TT/TL|TL/TT', re.IGNORECASE)
# Корень слова назначения → ось в названии: `вед.ось`, `рулевая`, `унив.ось`, `приц.`, `карьер`.
_AXIS_LABELS = (
    ('вед', 'Ведущая'),
    ('рул', 'Рулевая'),
    ('унив', 'Универсальная'),
    ('приц', 'Прицепная'),
    ('карьер', 'Карьерная'),
)


def layering_label(raw: object) -> str:
    """Слойность как `<N>PR`: `16`, `16PR`, `PR16` → `16PR`; без числа — пусто."""
    found = _DIGITS.search(str(raw or ''))
    return f'{found[0]}PR' if found else ''


def camera_label(raw: object, *, keep_tl: bool = True) -> str:
    """Камерность заглавными; `TL` у легковых шин не пишется (`keep_tl=False`): бескамерных 99 %."""
    camera = str(raw or '').strip()
    if not keep_tl and camera.upper() == _CAMERA_TL:
        return ''
    return camera.upper() if _CAMERA_CODE.fullmatch(camera) else camera


def axis_label(raw: object) -> str:
    """Ось/назначение из канонического словаря; незнакомое слово не пишется."""
    lower = str(raw or '').strip().lower()
    for root, label in _AXIS_LABELS:
        if lower.startswith(root):
            return label
    return ''
