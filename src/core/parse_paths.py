"""Очистка папки результатов через ConfigProvider, без импорта cfg."""

import shutil
from pathlib import Path

from core.config_provider import get_config_provider


def clear_result_folder() -> None:
    """Удалить содержимое result_folder, саму папку оставить."""
    folder = Path(get_config_provider().result_folder())
    if not folder.is_dir():
        return
    for entry in folder.iterdir():
        if entry.is_dir() and not entry.is_symlink():
            shutil.rmtree(entry)
            continue
        entry.unlink(missing_ok=True)
