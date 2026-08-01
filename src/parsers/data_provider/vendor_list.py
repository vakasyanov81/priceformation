"""
vendor list provider
"""

import json
from typing import NamedTuple

from cfg.main import MainConfig
from core.exceptions import CoreExceptionError
from core.file_reader import read_file


class VendorListConfigFileError(CoreExceptionError):
    """Exception for case when user config vendor list is failed to read"""


class VendorParams(NamedTuple):
    """vendor parameters"""

    enabled: int


class VendorListProviderBase:
    """Base data provider with supplier config"""

    def get_config_vendor_list(self):
        """Abstract method. Get config for vendor list."""
        raise NotImplementedError


class VendorListProviderFromUserConfig(VendorListProviderBase):
    """Base data provider with supplier config from user config file"""

    def get_config_vendor_list(self) -> dict:
        """get configuration for vendors"""
        return self.try_get_config_vendor_list()

    @classmethod
    def try_get_config_vendor_list(cls) -> dict:
        """safety get configuration for vendors"""
        try:
            return json.loads(read_file(MainConfig().vendor_list_file_path))
        except FileNotFoundError as exc:
            raise VendorListConfigFileError(
                f"Failed to read all vendor settings {MainConfig().vendor_list_file_name}"
            ) from exc
