# -*- coding: utf-8 -*-
"""
manufacturer aliases provider
"""
__author__ = "Kasyanov V.A."

import json

from cfg.main import MainConfig
from core.file_reader import try_read_file


class ManufacturerAliasesProviderBase:
    """Base data provider with manufacturer aliases"""

    def get_aliases(self) -> dict:
        """get manufacturer alias"""
        raise NotImplementedError


class ManufacturerAliasesProviderFromUserConfig(ManufacturerAliasesProviderBase):
    """Base data provider with manufacturer aliases from user config file"""

    def get_aliases(self) -> dict:
        """get manufacturer aliases"""
        return json.loads(
            try_read_file(MainConfig().manufacturer_aliases_file_path) or "{}"
        )
