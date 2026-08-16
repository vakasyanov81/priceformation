"""Title extras for four_tochki sheet 2 disks."""

import re
from typing import Any

from parsers.common_price_group_fields import disk_name_extras
from parsers.row_item.row_item import RowItem

_THICKNESS_RE = re.compile(r"\((\d+(?:[.,]\d+)?)\s*мм\)", re.IGNORECASE)


def join_title_parts(*parts: str) -> str:
    """Склеить куски title без пустых."""
    return " ".join(part for part in parts if part)


def thickness_from_name(name: str) -> str:
    """Толщина из скобок в наименовании: (15,5 мм)."""
    match = _THICKNESS_RE.search(name)
    if not match:
        return ""
    return match.group(1).replace(",", ".")


def fill_disk_thickness(row_item: RowItem) -> None:
    """Заполнить толщину из исходного наименования, если колонка пуста."""
    if row_item.disk_thickness:
        return
    thickness = thickness_from_name(row_item.title or "")
    if thickness:
        row_item.disk_thickness = thickness


def disk_name_suffix(name: str) -> str:
    """Толщина, усиление, камерность и различающие хвосты из наименования."""
    thickness = thickness_from_name(name)
    thick_label = "({0} мм)".format(thickness) if thickness else ""
    return join_title_parts(
        thick_label,
        "усил." if "усил" in name.lower() else "",
        _tube_label(name),
        disk_name_extras(name),
    )


def et_label(eet: Any) -> str:
    """ET с нулём: 0 не должен пропадать как falsy."""
    if eet is None or eet == "":
        return "ET"
    return "ET{0}".format(eet)


def disk_diameter(raw: Any) -> str:
    """Диаметр без хвостового .0, без порчи 22.5."""
    text = str(raw or "")
    if text.endswith(".0"):
        return text[:-2]
    return text


def _tube_label(name: str) -> str:
    lowered = name.lower()
    if "под камеру" in lowered:
        return "под камеру"
    if "б/к" in lowered:
        return "б/к"
    return ""
