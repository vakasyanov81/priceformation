"""configuration logic"""

from typing import TypeAlias
from . import main

ConfigType: TypeAlias = dict[str, type[main.MainConfig]]

__config__: ConfigType = {
    "main": main.get_config(),
}


class ConfigParamError(Exception):
    """wrong configuration Exception"""


class ConfigCompiler:
    """combine all config modules"""

    def __init__(self, config: ConfigType) -> None:
        """init"""
        self._config = config

    @property
    def main(self) -> main.MainConfig:
        """main section"""
        return main.get_config()()


def init_cfg(_cfg: ConfigType | None = None) -> ConfigCompiler:
    """get access to configuration"""
    return ConfigCompiler(_cfg or __config__)


__ALL__ = [init_cfg]
