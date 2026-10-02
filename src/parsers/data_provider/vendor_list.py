"""
vendor list provider
"""

from typing import Any

from domain.config_context import get_config_provider
from domain.exceptions import CoreExceptionError
from infrastructure.data.file_reader import read_json_file
from parsers.data_provider.json_fields import as_config_object
from parsers.data_provider.models import VendorConfigEntry

_CONFIG_FILE = 'vendor_list.json'


class VendorListConfigFileError(CoreExceptionError):
    """Exception for case when user config vendor list is failed to read"""


class VendorListProviderBase:
    """Base data provider with supplier config"""

    def get_config_vendor_list(self) -> dict[str, VendorConfigEntry]:
        """Abstract method. Get config for vendor list."""
        raise NotImplementedError


class VendorListProviderFromUserConfig(VendorListProviderBase):
    """Base data provider with supplier config from user config file"""

    def get_config_vendor_list(self) -> dict[str, VendorConfigEntry]:
        """get configuration for vendors"""
        return self.try_get_config_vendor_list()

    @classmethod
    def try_get_config_vendor_list(cls) -> dict[str, VendorConfigEntry]:
        """safety get configuration for vendors"""
        try:
            return cls._load_vendor_list_json()
        except FileNotFoundError as exc:
            raise VendorListConfigFileError(f'Failed to read all vendor settings {_CONFIG_FILE}') from exc

    @classmethod
    def _load_vendor_list_json(cls) -> dict[str, VendorConfigEntry]:
        """Read and parse vendor list JSON."""
        config_path = get_config_provider().config_file(_CONFIG_FILE)
        vendors = as_config_object(read_json_file(config_path), _CONFIG_FILE)
        return {code: cls._read_entry(entry, code) for code, entry in vendors.items()}

    @classmethod
    def _read_entry(cls, raw: Any, code: str) -> VendorConfigEntry:
        """Разобрать запись одного поставщика; путь до ключа — в сообщении."""
        return VendorConfigEntry.from_dict(raw, f'{_CONFIG_FILE} → {code}')
