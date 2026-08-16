"""Канон размера для ключа группировки."""

import re
from typing import Any, Tuple

from parsers.row_item.row_item import RowItem

_INCH_SIZE_RE = re.compile(r"(?i)(?<!\d)(\d{2,3})[xх](\d+(?:[.,]\d+)?)r(\d+(?:[.,]\d+)?)")
_DIAMETER_PREFIX_RE = re.compile(r"(?i)^(zr|rz|r)")


def canon_number(raw: Any) -> str:
    """Запятая → точка; 12.50 и 12.5 — одно число."""
    if raw is None or raw == "":
        return ""
    text = str(raw).replace(",", ".").strip()
    if not text:
        return ""
    try:
        number = float(text)
    except ValueError:
        return text
    if number.is_integer():
        return str(int(number))
    return str(number)


def canon_diameter(raw: Any) -> str:
    """R16 / ZR16 / 16 — один диаметр для ключа."""
    text = str(raw or "").strip()
    if not text:
        return ""
    return canon_number(_DIAMETER_PREFIX_RE.sub("", text, count=1))


def _inch_size_from_title(title: str | None) -> Tuple[str, str, str]:
    if not title:
        return "", "", ""
    match = _INCH_SIZE_RE.search(title)
    if not match:
        return "", "", ""
    ext_diameter, width, diameter = match.groups()
    return (
        canon_number(width),
        canon_number(diameter),
        canon_number(ext_diameter),
    )


def size_fields(row_item: RowItem) -> Tuple[str, str, str]:
    """width, diameter, внешний дюймовый диаметр — канон для ключа."""
    parsed = _inch_size_from_title(row_item.title)
    ext_raw = row_item.ext_diameter
    ext_diameter = canon_number(ext_raw) if ext_raw else parsed[2]
    return (
        canon_number(row_item.width) or parsed[0],
        canon_diameter(row_item.diameter) or parsed[1],
        ext_diameter,
    )
