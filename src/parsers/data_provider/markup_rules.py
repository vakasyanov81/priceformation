"""
markup rules provider
"""

import json
from typing import Dict, NamedTuple

from cfg.main import MainConfig
from core.exceptions import CoreExceptionError
from core.file_reader import read_file


class PriceRulesConfigFileError(CoreExceptionError):
    """Exception for case when user config price rules is failed to read"""


class MarkUpParams(NamedTuple):
    """mark up rule params"""

    min: float = 0
    max: float = 0
    percent: float = 0


class AbsoluteMarkUpRules(NamedTuple):
    """container for markup rule (absolute markup)"""

    min_absolute_markup: float = 0
    markup_percent: float = 0


class MarkupRules(NamedTuple):
    """container for vendor markup rules"""

    markup_rules: Dict[str, MarkUpParams]
    min_recommended_percent_markup: float = 0.0
    max_recommended_percent_markup: float = 0.0
    absolute_markup_rules: AbsoluteMarkUpRules = AbsoluteMarkUpRules(0, 0)


class MarkupRulesProviderBase:
    """Base markup rules data provider."""

    def __init__(self, supplier_name: str = None) -> None:
        """
        :param str supplier_name:
        """
        self._supplier_name = supplier_name

    @property
    def supplier_name(self):
        """supplier name"""
        return self._supplier_name

    def get_markup_data(self):
        """Abstract method. Get markup data."""
        raise NotImplementedError


class MarkupRulesProviderFromUserConfig(MarkupRulesProviderBase):
    """Markup rules data provider from user config file."""

    def get_markup_data(self) -> dict:
        """Get markup data from user config file."""
        return self.try_markup_data_for_supplier()

    def try_markup_data_for_supplier(self) -> dict:
        """Try get markup data."""
        try:
            return json.loads(read_file(self.get_file_path()))
        except FileNotFoundError as exc:
            raise PriceRulesConfigFileError(f"Filed to read vendor ({self.supplier_name}) settings.") from exc

    def get_file_path(self) -> str:
        """Get user config file path by supplier name or by default"""
        if self.supplier_name:
            return MainConfig().markup_rules_file_path.replace(
                MainConfig().markup_rules_file_name,
                f"{self.supplier_name}_{MainConfig().markup_rules_file_name}",
            )
        return MainConfig().markup_rules_file_path
