"""
manufacturer aliases provider
"""

import json
from functools import lru_cache
from typing import Any, cast

from cfg.main import MainConfig
from core.file_reader import read_file


def _filled_aliases(aliases: Any) -> Any:
    if not isinstance(aliases, list):
        return aliases
    filled: list[str] = []
    for alias in aliases:
        if not isinstance(alias, str):
            continue
        if alias.strip() == "":
            continue
        filled.append(alias)
    return filled


def drop_blank_aliases(aliases_map: dict[str, Any]) -> dict[str, Any]:
    """Remove empty and whitespace-only strings from brand alias lists."""
    cleaned: dict[str, Any] = {}
    for brand, entry in aliases_map.items():
        if isinstance(entry, dict):
            record = dict(entry)
            record["aliases"] = _filled_aliases(record.get("aliases", []))
            cleaned[brand] = record
            continue
        cleaned[brand] = _filled_aliases(entry)
    return cleaned


def aliases_for_finder(
    aliases_map: dict[str, Any],
) -> dict[str, tuple[str, ...] | str]:
    """Alias lists only: Finder ignores grouping metadata."""
    finder_map: dict[str, tuple[str, ...] | str] = {}
    for brand, entry in aliases_map.items():
        raw: Any = entry
        if isinstance(entry, dict):
            raw = entry.get("aliases", [])
        if isinstance(raw, str):
            raw = [raw]
        if isinstance(raw, tuple):
            raw = list(raw)
        if isinstance(raw, list):
            finder_map[brand] = tuple(_filled_aliases(raw))
            continue
        finder_map[brand] = ()
    return finder_map


def manufacturer_group(
    manufacturer: str | None,
    aliases_map: dict[str, Any] | None = None,
) -> str:
    """Canon for grouping: JSON group, alias owner, or the brand key in lowercase."""
    name = (manufacturer or "").strip()
    if not name or not aliases_map:
        return name.lower()
    lookup: dict[str, str] = {}
    for brand, entry in aliases_map.items():
        lookup[brand.lower()] = brand.lower()
        if isinstance(entry, dict) and entry.get("group"):
            lookup[brand.lower()] = str(entry["group"]).lower()
        for alias in aliases_for_finder({brand: entry})[brand]:
            lookup[str(alias).lower()] = lookup[brand.lower()]
    return lookup.get(name.lower(), name.lower())


@lru_cache(maxsize=1)
def load_aliases_map() -> dict[str, Any]:
    """Load manufacturer aliases from user config; empty if the file is missing."""
    try:
        return ManufacturerAliasesProviderFromUserConfig().get_aliases()
    except FileNotFoundError:
        return {}


class ManufacturerAliasesProviderBase:
    """Base data provider with manufacturer aliases"""

    def get_aliases(self) -> dict[str, Any]:
        """get manufacturer alias"""
        raise NotImplementedError


class ManufacturerAliasesProviderFromUserConfig(ManufacturerAliasesProviderBase):
    """Base data provider with manufacturer aliases from user config file"""

    def get_aliases(self) -> dict[str, Any]:
        """get manufacturer aliases"""
        raw: str = read_file(MainConfig().manufacturer_aliases_file_path)
        return drop_blank_aliases(cast(dict[str, Any], json.loads(raw)))
