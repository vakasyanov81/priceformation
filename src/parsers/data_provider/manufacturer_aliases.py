"""
manufacturer aliases provider
"""

import json
from typing import Any, cast

from cfg.main import MainConfig
from core.file_reader import read_file


class ManufacturerAliasesProviderBase:
    """Base data provider with manufacturer aliases"""

    def get_aliases(self) -> dict[str, Any]:
        """get manufacturer alias"""
        raise NotImplementedError


class ManufacturerAliasesProviderFromUserConfig(ManufacturerAliasesProviderBase):
    """Base data provider with manufacturer aliases from user config file"""

    def get_aliases(self) -> dict[str, Any]:
        """get manufacturer aliases"""
        return cast(dict[str, Any], json.loads(read_file(MainConfig().manufacturer_aliases_file_path)))
