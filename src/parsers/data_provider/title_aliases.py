"""
title aliases provider
"""

import json
from typing import Any

from domain.protocols import ConfigProvider
from infrastructure.data.file_reader import read_file

_CONFIG_FILE = 'title_aliases.json'


def invert_title_aliases(title_aliases: dict[str, Any]) -> dict[str, Any]:
    """Invert {correct: [incorrect, ...]} to {incorrect: correct}."""
    inverted: dict[str, Any] = {}
    for correct_title, incorrect_titles in title_aliases.items():
        for incorrect_title in incorrect_titles:
            inverted[incorrect_title] = correct_title
    return inverted


def load_title_aliases(supplier_name: str, config_provider: ConfigProvider) -> dict[str, Any]:
    """Load inverted title aliases for supplier; empty if the file is missing."""
    try:
        return TitleAliasesProviderFromUserConfig(supplier_name, config_provider).get_aliases()
    except FileNotFoundError:
        return {}


class TitleAliasesProviderBase:
    """Base data provider with title aliases."""

    def get_aliases(self) -> dict[str, Any]:
        """get title aliases"""
        raise NotImplementedError


class TitleAliasesProviderFromUserConfig(TitleAliasesProviderBase):
    """Title aliases from user config file, inverted for lookup."""

    def __init__(self, supplier_name: str, config_provider: ConfigProvider) -> None:
        self._supplier_name = supplier_name
        self._config_provider = config_provider

    def get_aliases(self) -> dict[str, Any]:
        """Read JSON and invert map for this supplier name."""
        raw: str = read_file(self._config_provider.config_file(_CONFIG_FILE))
        payload: Any = json.loads(raw) or {}
        return invert_title_aliases(payload.get(self._supplier_name) or {})
