"""
manufacturer aliases provider
"""

import json
from typing import Any, cast

from domain.protocols import ConfigProvider
from infrastructure.data.file_reader import read_file

_CONFIG_FILE = 'manufacturer_aliases.json'
_ALIASES_CACHE: dict[str, dict[str, Any]] = {}


def _filled_aliases(aliases: Any) -> Any:
    if not isinstance(aliases, list):
        return aliases
    filled: list[str] = []
    for alias in aliases:
        if not isinstance(alias, str):
            continue
        if alias.strip() == '':
            continue
        filled.append(alias)
    return filled


def drop_blank_aliases(aliases_map: dict[str, Any]) -> dict[str, Any]:
    """Remove empty and whitespace-only strings from brand alias lists."""
    cleaned: dict[str, Any] = {}
    for brand, entry in aliases_map.items():
        if isinstance(entry, dict):
            record = dict(entry)
            record['aliases'] = _filled_aliases(record.get('aliases', []))
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
            raw = entry.get('aliases', [])
        if isinstance(raw, str):
            raw = [raw]
        if isinstance(raw, tuple):
            raw = list(raw)
        if isinstance(raw, list):
            finder_map[brand] = tuple(_filled_aliases(raw))
            continue
        finder_map[brand] = ()
    return finder_map


def load_aliases_map(config_provider: ConfigProvider) -> dict[str, Any]:
    """Load manufacturer aliases from user config (cached per file path); empty if the file is missing."""
    path = config_provider.config_file(_CONFIG_FILE)
    if path not in _ALIASES_CACHE:
        try:
            _ALIASES_CACHE[path] = ManufacturerAliasesProviderFromUserConfig(config_provider).get_aliases()
        except FileNotFoundError:
            _ALIASES_CACHE[path] = {}
    return _ALIASES_CACHE[path]


def clear_manufacturer_aliases_cache() -> None:
    """Drop the process-level manufacturer aliases cache."""
    _ALIASES_CACHE.clear()


class ManufacturerAliasesProviderBase:
    """Base data provider with manufacturer aliases"""

    def get_aliases(self) -> dict[str, Any]:
        """get manufacturer alias"""
        raise NotImplementedError


class ManufacturerAliasesProviderFromUserConfig(ManufacturerAliasesProviderBase):
    """Base data provider with manufacturer aliases from user config file"""

    def __init__(self, config_provider: ConfigProvider) -> None:
        self._config_provider = config_provider

    def get_aliases(self) -> dict[str, Any]:
        """get manufacturer aliases"""
        raw: str = read_file(self._config_provider.config_file(_CONFIG_FILE))
        return drop_blank_aliases(cast(dict[str, Any], json.loads(raw)))
