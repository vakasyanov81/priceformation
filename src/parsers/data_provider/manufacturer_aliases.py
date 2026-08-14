"""
manufacturer aliases provider
"""

import json
from typing import Any, cast

from cfg.main import MainConfig
from core.file_reader import read_file


def _is_filled_alias(alias: Any) -> bool:
    return isinstance(alias, str) and alias.strip() != ""


def _filled_aliases(aliases: Any) -> Any:
    if not isinstance(aliases, list):
        return aliases
    return [alias for alias in aliases if _is_filled_alias(alias)]


def drop_blank_aliases(aliases_map: dict[str, Any]) -> dict[str, Any]:
    """Remove empty and whitespace-only strings from brand alias lists."""
    return {brand: _filled_aliases(aliases) for brand, aliases in aliases_map.items()}


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
