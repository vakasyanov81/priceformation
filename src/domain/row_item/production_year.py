"""Год выпуска шины по названию позиции."""

import re

# «старше N лет» — старше любого явного года выпуска; число в поле — условная метка, а не год.
OLDEST_YEAR = 1
_YEAR_RE = re.compile(r'(?<!\d)(20\d{2})\s*г\.?\s*в\b', re.IGNORECASE)
_OLDER_RE = re.compile(r'\d+\s+года?\s+и\s+старше', re.IGNORECASE)


def production_year(title: str | None) -> int | None:
    """Год выпуска из «2023г.в.», «2022 г.в.»; «2 года и старше» → OLDEST_YEAR; нет признака → None."""
    text = title or ''
    match = _YEAR_RE.search(text)
    if match:
        return int(match[1])
    return OLDEST_YEAR if _OLDER_RE.search(text) else None
