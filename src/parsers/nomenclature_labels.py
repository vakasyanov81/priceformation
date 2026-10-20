"""Каноническое написание токенов названия шины: слойность, камерность, `XL`, сезонные маркеры, ось."""

import re

_DIGITS = re.compile(r'\d+')
_CAMERA_CODE = re.compile(r'TT|TL|TTF|TT/TL|TL/TT', re.IGNORECASE)
_RUN_FLAT = re.compile(r'(?<!\S)(?:RunFlat|Run[\s-]?Flat|RFT)(?=\s|$)', re.IGNORECASE)
_XL = re.compile(r'(?<!\w)xl(?!\w)', re.IGNORECASE)
# `M+S` и `M&S` — один маркер; `3PMSF` — отдельный: зимний сертификат.
_SEASON_MARK = re.compile(r'(?<!\S)(M[+&]S|3PMSF)(?!\S)', re.IGNORECASE)
_SEASON_MARKS = ('M+S', '3PMSF')
_RUN_FLAT_YES = frozenset(('да', 'yes', '1', 'true'))
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


def camera_label(raw: object) -> str:
    """Камерность заглавными: `TT`, `TL`, `TTF`; остальное как есть."""
    camera = str(raw or '').strip()
    return camera.upper() if _CAMERA_CODE.fullmatch(camera) else camera


def xl_label(*sources: object) -> str:
    """`XL`, если он есть хотя бы в одном из текстов; иначе пусто."""
    text = ' '.join(str(source or '') for source in sources)
    return 'XL' if _XL.search(text) else ''


def season_marks_label(*sources: object) -> tuple[str, ...]:
    """`M+S` и `3PMSF` из текстов (название, надпись на боковине) в каноническом порядке; нет маркера — пусто."""
    found = {
        'M+S' if match[1][0] in 'Mm' else '3PMSF'
        for source in sources
        for match in _SEASON_MARK.finditer(str(source or ''))
    }
    return tuple(mark for mark in _SEASON_MARKS if mark in found)


def axis_label(raw: object) -> str:
    """Ось/назначение из канонического словаря; незнакомое слово не пишется."""
    lower = str(raw or '').strip().lower()
    for root, label in _AXIS_LABELS:
        if lower.startswith(root):
            return label
    return ''


def run_flat_label(flag: object, title: str | None) -> str:
    """`RunFlat`, если колонка прайса отмечена («да») или в названии есть `RFT`/`Run Flat`/`Run-Flat`; иначе пусто."""
    marked = str(flag or '').strip().lower() in _RUN_FLAT_YES
    return 'RunFlat' if marked or _RUN_FLAT.search(title or '') else ''
