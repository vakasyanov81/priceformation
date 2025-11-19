# -*- coding: utf-8 -*-
"""configuration logic"""
__author__ = "Kasyanov V.A."

from . import main

__config__ = {
    "main": main.get_config(),
}


class ConfigParamError(Exception):
    """wrong configuration Exception"""


class ConfigCompiler:
    """combine all config modules"""

    def __init__(self, config: dict, is_unit_test_mode=False):
        """init"""
        self._config = config
        self.is_unit_test_mode = is_unit_test_mode

    @property
    def main(self) -> main.MainConfig:
        """main section"""
        return self._config.get("main")()


def init_cfg(_cfg=None):
    """get access to configuration"""
    return ConfigCompiler(_cfg or __config__)


__ALL__ = [init_cfg]
