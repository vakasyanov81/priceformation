"""
markup rules provider
"""

from pathlib import Path

from domain.config_context import get_config_provider
from domain.exceptions import CoreExceptionError
from infrastructure.data.file_reader import read_json_file
from parsers.data_provider.models import MarkupRulesConfig

_CONFIG_FILE = 'markup_rules.json'


class PriceRulesConfigFileError(CoreExceptionError):
    """Exception for case when user config price rules is failed to read"""


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

    def get_markup_data(self) -> MarkupRulesConfig:
        """Abstract method. Get markup data."""
        raise NotImplementedError


class MarkupRulesProviderFromUserConfig(MarkupRulesProviderBase):
    """Markup rules data provider from user config file."""

    def get_markup_data(self) -> MarkupRulesConfig:
        """Get markup data from user config file."""
        return self.try_markup_data_for_supplier()

    def try_markup_data_for_supplier(self) -> MarkupRulesConfig:
        """Try get markup data."""
        try:
            return self._load_markup_json()
        except FileNotFoundError as exc:
            raise PriceRulesConfigFileError(f'Filed to read vendor ({self.supplier_name}) settings.') from exc

    def _load_markup_json(self) -> MarkupRulesConfig:
        """Read and parse markup JSON file."""
        file_path = self.get_file_path()
        return MarkupRulesConfig.from_dict(read_json_file(file_path), Path(file_path).name)

    def get_file_path(self) -> str:
        """Get user config file path by supplier name or by default"""
        file_name = _CONFIG_FILE
        if self.supplier_name:
            file_name = f'{self.supplier_name}_{_CONFIG_FILE}'
        return get_config_provider().config_file(file_name)
