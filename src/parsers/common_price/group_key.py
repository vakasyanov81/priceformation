"""Ключ группировки позиций прайса."""

from typing import Any

from domain.row_item.row_item import RowItem
from parsers.common_price.group_fields import (
    brand_key_parts,
    camera_key,
    disk_extras_key,
    sidewall,
    yes_flag,
)
from parsers.common_price.model import clear_model
from parsers.common_price.size import canon_number, size_fields
from parsers.common_price.title_flags import valve_key
from parsers.data_provider.manufacturer_aliases import load_aliases_map
from parsers.strategies.normalize import replace_homoglyphs

# Позиция модели в ключе `group_key` (сверяется тестом): по ней группировщик склеивает модели с лишними словами.
MODEL_KEY_INDEX = 6


def sanitize_value(price_list_values: list[Any]) -> tuple[str, ...]:
    """Преобразует значения в строки, корректно обрабатывая None."""
    return tuple('' if price_list_val is None else str(price_list_val) for price_list_val in price_list_values)


def define_intimacy(row_item: RowItem) -> str | None:
    """Определить камерность (TL/TT/TTF) из title."""

    def is_float_diameter(diameter: Any) -> bool:
        diameter_str = str(diameter or 0).replace(',', '.')
        try:
            return not float(diameter_str).is_integer()
        except ValueError, TypeError:
            return False

    chunks = replace_homoglyphs((row_item.identity.title or '').lower()).split()
    for intimacy in ('tl', 'tt', 'ttf'):
        if intimacy in chunks:
            return intimacy.upper()

    type_prod = (row_item.vendor.type_production or '').lower()
    if 'грузовая' in type_prod and is_float_diameter(row_item.tire.diameter):
        return 'TL'
    return None


def _group_key_parts(row_item: RowItem, aliases_map: dict[str, Any]) -> list[Any]:
    """Значения полей для ключа группировки."""
    mark, brand, mark_group, key_brand = brand_key_parts(row_item, aliases_map)
    intimacy = (row_item.tire.intimacy or define_intimacy(row_item) or '').upper()
    return [
        (row_item.vendor.type_production or '').lower(),
        *size_fields(row_item),
        row_item.tire.index_velocity,
        row_item.tire.index_load,
        clear_model(row_item.identity.model, mark, brand),
        mark_group,
        row_item.tire.layering,
        key_brand,
        camera_key(row_item, intimacy),
        canon_number(row_item.disk.disk_thickness),
        yes_flag(row_item.tire.run_flat),
        sidewall(row_item.tire.inscription_on_the_side),
        disk_extras_key(row_item),
        valve_key(row_item),
    ]


def group_key(
    row_item: RowItem,
    aliases_map: dict[str, Any] | None = None,
) -> tuple[str, ...]:
    """Ключ группировки."""
    mapping = load_aliases_map() if aliases_map is None else aliases_map
    return sanitize_value(_group_key_parts(row_item, mapping))
