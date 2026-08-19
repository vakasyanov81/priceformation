"""configuration logic"""

from pathlib import Path

from core.log_paths import LogPaths, configure_log_paths
from core.parse_paths import ParsePaths, configure_parse_paths

from . import main

type ConfigType = dict[str, type[main.MainConfig]]

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
    compiler = ConfigCompiler(_cfg or __config__)
    _configure_core_log_paths(compiler.main)
    _configure_core_parse_paths(compiler.main)
    return compiler


def _configure_core_log_paths(main_cfg: main.MainConfig) -> None:
    """Push log locations into core so core does not import cfg."""
    configure_log_paths(
        LogPaths(
            folder=main_cfg.log_folder_path,
            log_file=main_cfg.current_log_file_path,
            err_file=main_cfg.current_err_log_file_path,
        )
    )


def _configure_core_parse_paths(main_cfg: main.MainConfig) -> None:
    """Push price and parse_config folders into core so parsers do not import cfg."""
    configure_parse_paths(
        ParsePaths(
            file_prices_folder=str(Path(main_cfg.project_root) / main_cfg.folder_file_prices),
            user_config_folder=main_cfg.user_config_folder_path,
        )
    )


__ALL__ = [init_cfg]
