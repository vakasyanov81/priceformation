"""Canon manufacturer name for price grouping."""

from typing import Any, cast

from parsers.data_provider.manufacturer_aliases import aliases_for_finder

_GROUP_CACHE: list[Any] = [None, {}]


def _build_lookup(aliases_map: dict[str, Any]) -> dict[str, str]:
    """Lowercased brand/alias -> grouping canon."""
    grouped: dict[str, str] = {}
    finder_aliases = aliases_for_finder(aliases_map)
    for brand, entry in aliases_map.items():
        if isinstance(entry, dict) and entry.get("group"):
            grouped[brand.lower()] = str(entry["group"]).lower()
        else:
            grouped[brand.lower()] = brand.lower()
        for alias in finder_aliases[brand]:
            grouped[str(alias).lower()] = grouped[brand.lower()]
    return grouped


def manufacturer_group(
    manufacturer: str | None,
    aliases_map: dict[str, Any] | None = None,
) -> str:
    """Canon for grouping: JSON group, alias owner, or the brand key in lowercase."""
    name = (manufacturer or "").strip()
    if not name or not aliases_map:
        return name.lower()
    map_id = id(aliases_map)
    if map_id != _GROUP_CACHE[0]:
        _GROUP_CACHE[0] = map_id
        _GROUP_CACHE[1] = _build_lookup(aliases_map)
    grouped = cast(dict[str, str], _GROUP_CACHE[1])
    return grouped.get(name.lower(), name.lower())
