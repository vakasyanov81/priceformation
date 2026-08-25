"""
manufacturer aliases provider
"""

import json
from functools import lru_cache
from typing import Any, cast

from core.file_reader import read_file
from core.parse_paths import get_parse_paths

_CONFIG_FILE = "manufacturer_aliases.json"


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


@lru_cache(maxsize=1)
def load_aliases_map() -> dict[str, Any]:
    """Load manufacturer aliases from user config; empty if the file is missing."""
    try:
        return ManufacturerAliasesProviderFromUserConfig().get_aliases()
    except FileNotFoundError:
        return {}


def clear_manufacturer_aliases_cache() -> None:
    """Drop the process-level manufacturer aliases cache."""
    load_aliases_map.cache_clear()


class ManufacturerAliasesProviderBase:
    """Base data provider with manufacturer aliases"""

    def get_aliases(self) -> dict[str, Any]:
        """get manufacturer alias"""
        raise NotImplementedError


class ManufacturerAliasesProviderFromUserConfig(ManufacturerAliasesProviderBase):
    """Base data provider with manufacturer aliases from user config file"""

    def get_aliases(self) -> dict[str, Any]:
        """get manufacturer aliases"""
        raw: str = read_file(get_parse_paths().config_file(_CONFIG_FILE))
        return drop_blank_aliases(cast(dict[str, Any], json.loads(raw)))
