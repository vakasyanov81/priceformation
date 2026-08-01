"""Ключ группировки позиций прайса."""

from typing import Any, List, Optional, Tuple

from parsers.row_item.row_item import RowItem


def sanitize_value(price_list_values: List[Any]) -> Tuple[str, ...]:
    """Преобразует значения в строки, корректно обрабатывая None."""
    return tuple("" if price_list_val is None else str(price_list_val) for price_list_val in price_list_values)


def clear_model(model: Optional[str]) -> str:
    """Очистка названия модели от пробелов и префиксов до дефиса."""
    if not model:
        return ""

    model = model.replace(" ", "")
    parts = model.split("-")

    # Если есть дефис, берем вторую часть, иначе всю строку
    return parts[1] if len(parts) > 1 else parts[0]


def _is_float_diameter(diameter: Any) -> bool:
    """Диаметр не целое число (например 15.3)."""
    diameter_str = str(diameter or 0).replace(",", ".")
    try:
        return not float(diameter_str).is_integer()
    except (ValueError, TypeError):
        return False


def define_intimacy(row_item: RowItem) -> Optional[str]:
    """Определить камерность (TL/TT/TTF) из title."""
    chunks = (row_item.title or "").lower().split()
    for intimacy in ("tl", "tt", "ttf"):
        if intimacy in chunks:
            return intimacy.upper()

    type_prod = (row_item.type_production or "").lower()
    if "грузовая" in type_prod and _is_float_diameter(row_item.diameter):
        return "TL"
    return None


def _group_key_parts(row_item: RowItem) -> List[Any]:
    """Значения полей для ключа группировки."""
    mark = (row_item.manufacturer or "").lower()
    brand = (row_item.brand or "").lower()
    brand = "" if brand == mark else brand
    return [
        (row_item.type_production or "").lower(),
        row_item.width,
        row_item.diameter,
        row_item.height_percent,
        row_item.index_velocity,
        row_item.index_load,
        clear_model(row_item.model),
        mark,
        row_item.axis,
        row_item.layering,
        row_item.slot_count,
        row_item.central_diameter,
        row_item.slot_diameter,
        row_item.color,
        brand,
        row_item.eet,
        row_item.intimacy or define_intimacy(row_item),
    ]


def group_key(row_item: RowItem) -> Tuple[str, ...]:
    """Ключ группировки."""
    return sanitize_value(_group_key_parts(row_item))
