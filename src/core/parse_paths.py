"""Price, parse_config, and result folders; configured from cfg, never imported from it."""

from dataclasses import dataclass
from pathlib import Path


class ParsePathsNotConfiguredError(RuntimeError):
    """Raised when get_parse_paths runs before configure_parse_paths."""

    def __init__(self) -> None:
        super().__init__("Parse paths are not configured")


@dataclass(frozen=True)
class ParsePaths:
    """Folders for supplier prices, parse_config, and written result xlsx."""

    file_prices_folder: str
    user_config_folder: str
    result_folder: str

    def config_file(self, file_name: str) -> str:
        """Absolute path to a file inside parse_config."""
        return str(Path(self.user_config_folder) / file_name)


class _CurrentParsePaths:
    """Process-wide parse locations without a cfg import."""

    configured: ParsePaths | None = None


def configure_parse_paths(paths: ParsePaths) -> None:
    """Set folders used by data_provider, FilePricesSource, and writer."""
    _CurrentParsePaths.configured = paths


def get_parse_paths() -> ParsePaths:
    """Return configured folders; raise if init_cfg has not run."""
    paths = _CurrentParsePaths.configured
    if paths is None:
        raise ParsePathsNotConfiguredError()
    return paths
