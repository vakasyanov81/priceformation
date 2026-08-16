"""Доп. поля ключа группировки: PCD, камера, RunFlat, боковина, хвосты диска."""

from typing import Any

from parsers.data_provider.manufacturer_aliases import manufacturer_group
from parsers.row_item.disk_name_extras import disk_name_extras
from parsers.row_item.row_item import RowItem

_DISTINGUISHING_INTIMACY = frozenset(("TT", "TTF", "TT-ONLY"))
_YES_FLAGS = frozenset(("да", "yes", "1", "true", "runflat"))
_DISK_KIND = "диск"


def brand_key_parts(
    row_item: RowItem,
    aliases_map: dict[str, Any],
) -> tuple[str, str, str, str]:
    """manufacturer/brand для модели и ключа."""
    mark = (row_item.manufacturer or "").lower()
    brand = (row_item.brand or "").lower()
    if brand == mark:
        brand = ""
    mark_group = manufacturer_group(row_item.manufacturer, aliases_map)
    key_brand = manufacturer_group(row_item.brand, aliases_map)
    if not key_brand or key_brand == mark_group:
        key_brand = ""
    return mark, brand, mark_group, key_brand


def yes_flag(raw: Any) -> str:
    """Да/RunFlat → одна метка."""
    text = str(raw or "").strip().lower()
    return "да" if text in _YES_FLAGS else ""


def sidewall(raw: Any) -> str:
    """Надпись на боковине: M+S vs 3PMSF."""
    return str(raw or "").strip().lower()


def camera_from_field(camera_type: Any) -> str | None:
    """TT / TTF / «только шина»; TL не отличает."""
    text = str(camera_type or "").strip()
    if not text:
        return None
    upper = text.upper()
    if "ТОЛЬКО" in upper:
        return "TT-ONLY"
    if upper.startswith("TTF"):
        return "TTF"
    if upper.startswith("TT"):
        return "TT"
    return None


def camera_key(row_item: RowItem, intimacy: str | None) -> str | None:
    """Камерность из поля поставщика, иначе из title."""
    from_field = camera_from_field(row_item.camera_type)
    if from_field:
        return from_field
    token = (intimacy or "").upper()
    if token in _DISTINGUISHING_INTIMACY:
        return token
    return None


def disk_extras_key(row_item: RowItem) -> str:
    """Хвосты диска в ключе; пусто если не диск или хвоста нет."""
    kind = (row_item.type_production or "").lower()
    if _DISK_KIND not in kind:
        return ""
    return disk_name_extras(row_item.title or "").lower()
