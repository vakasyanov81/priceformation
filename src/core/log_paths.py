"""Log file locations; configured from cfg, never imported from it."""

import datetime
from dataclasses import dataclass
from pathlib import Path

_LOG_FILE_TEMPLATE = 'log_{date}.log'
_ERR_FILE_TEMPLATE = 'error_{date}.log'


class LogPathsNotConfiguredError(RuntimeError):
    """Raised when get_log_paths runs before configure_log_paths."""

    def __init__(self) -> None:
        super().__init__('Log paths are not configured')


@dataclass(frozen=True)
class LogPaths:
    """Folder and dated log / error file paths."""

    folder: str
    log_file: str
    err_file: str

    @classmethod
    def for_folder(cls, folder: str) -> LogPaths:
        """Log folder with today's log and error files inside it."""
        today = datetime.date.today()
        return cls(
            folder=folder,
            log_file=str(Path(folder) / _LOG_FILE_TEMPLATE.format(date=today)),
            err_file=str(Path(folder) / _ERR_FILE_TEMPLATE.format(date=today)),
        )


class _CurrentLogPaths:
    """Process-wide log locations without a cfg import."""

    configured: LogPaths | None = None


def configure_log_paths(paths: LogPaths) -> None:
    """Set paths used by init_log and resolve_log_path."""
    _CurrentLogPaths.configured = paths


def get_log_paths() -> LogPaths:
    """Return configured paths; raise if init_cfg has not run."""
    paths = _CurrentLogPaths.configured
    if paths is None:
        raise LogPathsNotConfiguredError()
    return paths
