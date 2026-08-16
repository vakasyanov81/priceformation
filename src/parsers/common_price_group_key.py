"""Ключ группировки позиций прайса."""

from typing import Any, List, Optional, Tuple

from parsers.common_price_group_fields import (
    brand_key_parts,
    camera_key,
    disk_extras_key,
    sidewall,
    yes_flag,
)
from parsers.common_price_size import canon_number, size_fields
from parsers.data_provider.manufacturer_aliases import load_aliases_map
from parsers.row_item.row_item import RowItem

_KNOWN_MODEL_PREFIXES = ("кама", "kama")
_PREFIX_SEPARATORS = "- "


def sanitize_value(price_list_values: List[Any]) -> Tuple[str, ...]:
    """Преобразует значения в строки, корректно обрабатывая None."""
    return tuple("" if price_list_val is None else str(price_list_val) for price_list_val in price_list_values)


def clear_model(
    model: Optional[str],
    manufacturer: Optional[str] = None,
    brand: Optional[str] = None,
) -> str:
    """Очистка модели: нижний регистр, без пробелов, без префикса бренда."""
    if not model:
        return ""
    normalized = model.lower()
    for prefix in _model_prefixes(manufacturer, brand):
        normalized = _lstrip_brand_prefix(normalized, prefix)
    return normalized.replace(" ", "")


def _lstrip_brand_prefix(model: str, prefix: str) -> str:
    """Убрать префикс бренда, если за ним разделитель или конец строки."""
    if not model.startswith(prefix):
        return model
    rest = model[len(prefix) :]
    if not rest:
        return ""
    if rest[0] in _PREFIX_SEPARATORS:
        return rest.lstrip(_PREFIX_SEPARATORS)
    return model


def _model_prefixes(manufacturer: Optional[str], brand: Optional[str]) -> List[str]:
    """Префиксы бренда: известные и имена manufacturer/brand, длинные раньше."""
    names = (manufacturer, brand, *_KNOWN_MODEL_PREFIXES)
    unique = {name.lower().strip() for name in names if name}
    return sorted(unique, key=len, reverse=True)


def define_intimacy(row_item: RowItem) -> Optional[str]:
    """Определить камерность (TL/TT/TTF) из title."""

    def is_float_diameter(diameter: Any) -> bool:
        diameter_str = str(diameter or 0).replace(",", ".")
        try:
            return not float(diameter_str).is_integer()
        except (ValueError, TypeError):
            return False

    chunks = (row_item.title or "").lower().split()
    for intimacy in ("tl", "tt", "ttf"):
        if intimacy in chunks:
            return intimacy.upper()

    type_prod = (row_item.type_production or "").lower()
    if "грузовая" in type_prod and is_float_diameter(row_item.diameter):
        return "TL"
    return None


def _group_key_parts(row_item: RowItem, aliases_map: dict[str, Any]) -> List[Any]:
    """Значения полей для ключа группировки."""
    mark, brand, mark_group, key_brand = brand_key_parts(row_item, aliases_map)
    intimacy = (row_item.intimacy or define_intimacy(row_item) or "").upper()
    return [
        (row_item.type_production or "").lower(),
        *size_fields(row_item),
        canon_number(row_item.height_percent),
        row_item.index_velocity,
        row_item.index_load,
        clear_model(row_item.model, mark, brand),
        mark_group,
        row_item.layering,
        key_brand,
        camera_key(row_item, intimacy),
        canon_number(row_item.disk_thickness),
        yes_flag(row_item.run_flat),
        sidewall(row_item.inscription_on_the_side),
        disk_extras_key(row_item),
    ]


def group_key(
    row_item: RowItem,
    aliases_map: dict[str, Any] | None = None,
) -> Tuple[str, ...]:
    """Ключ группировки."""
    mapping = load_aliases_map() if aliases_map is None else aliases_map
    return sanitize_value(_group_key_parts(row_item, mapping))
