"""
markup rules provider
"""

import json
from typing import Any, NamedTuple, cast

from core.exceptions import CoreExceptionError
from core.file_reader import read_file
from core.parse_paths import get_parse_paths

_CONFIG_FILE = "markup_rules.json"

ABSOLUTE_MODE_MULTIPLIER = "multiplier"
ABSOLUTE_MODE_DELTA = "delta"


class PriceRulesConfigFileError(CoreExceptionError):
    """Exception for case when user config price rules is failed to read"""


class MarkUpParams(NamedTuple):
    """mark up rule params"""

    min: float = 0
    max: float = 0
    percent_markup: float = 0


def markup_params_from_rule(rule: dict[str, Any]) -> MarkUpParams:
    """JSON rule → MarkUpParams. Accepts ``percent`` or ``percent_markup``."""
    percent = rule.get("percent_markup", rule.get("percent", 0))
    return MarkUpParams(
        min=rule.get("min", 0),
        max=rule.get("max", 0),
        percent_markup=percent,
    )


class AbsoluteMarkUpRules(NamedTuple):
    """container for markup rule (absolute markup)"""

    min_absolute_markup: float = 0
    markup_percent: float = 0
    mode: str = ABSOLUTE_MODE_MULTIPLIER


class MarkupRules(NamedTuple):
    """container for vendor markup rules"""

    markup_rules: dict[str, dict[str, Any]]
    min_recommended_percent_markup: float = 0
    max_recommended_percent_markup: float = 0
    absolute_markup_rules: AbsoluteMarkUpRules = AbsoluteMarkUpRules(0, 0)
    replace_small_recommended: bool = False

    def should_replace_with_map(
        self,
        price_recommended: float | None,
        recommended_is_small: bool,
    ) -> bool:
        """Mim keeps RRC when present; Zapaska still applies the min-% check."""
        if price_recommended and not self.replace_small_recommended:
            return False
        return recommended_is_small


class MarkupRulesProviderBase:
    """Base markup rules data provider."""

    def __init__(self, supplier_name: str | None = None) -> None:
        """
        :param str supplier_name:
        """
        self._supplier_name = supplier_name

    @property
    def supplier_name(self) -> str | None:
        """supplier name"""
        return self._supplier_name

    def get_markup_data(self) -> dict[str, Any]:
        """Abstract method. Get markup data."""
        raise NotImplementedError


class MarkupRulesProviderFromUserConfig(MarkupRulesProviderBase):
    """Markup rules data provider from user config file."""

    def get_markup_data(self) -> dict[str, Any]:
        """Get markup data from user config file."""
        return self.try_markup_data_for_supplier()

    def try_markup_data_for_supplier(self) -> dict[str, Any]:
        """Try get markup data."""
        try:
            return self._load_markup_json()
        except FileNotFoundError as exc:
            raise PriceRulesConfigFileError(f"Filed to read vendor ({self.supplier_name}) settings.") from exc

    def _load_markup_json(self) -> dict[str, Any]:
        """Read and parse markup JSON file."""
        raw: str = read_file(self.get_file_path())
        return cast(dict[str, Any], json.loads(raw))

    def get_file_path(self) -> str:
        """Get user config file path by supplier name or by default"""
        file_name = _CONFIG_FILE
        if self.supplier_name:
            file_name = f"{self.supplier_name}_{_CONFIG_FILE}"
        return get_parse_paths().config_file(file_name)
