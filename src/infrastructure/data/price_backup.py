"""Копия папки прайсов во временную папку ОС: точка сравнения «до обновления»."""

import shutil
import tempfile
from collections.abc import Callable
from pathlib import Path

type IgnoreRule = Callable[[str, list[str]], set[str]]

BACKUP_FOLDER_NAME = 'file_prices_old'


def default_backup_folder() -> Path:
    """Папка копии во временном каталоге ОС (`/tmp` на Linux, `%TEMP%` на Windows)."""
    return Path(tempfile.gettempdir()) / BACKUP_FOLDER_NAME


def backup_prices(source: Path, target: Path, *, skip: Path | None = None) -> None:
    """Заменить `target` копией `source`; папка `skip` (результаты прошлых разборов) не копируется."""
    if target.exists():
        shutil.rmtree(target)
    if not source.is_dir():
        target.mkdir(parents=True)
        return
    shutil.copytree(source, target, ignore=_skip_folder(skip))


def _skip_folder(skip: Path | None) -> IgnoreRule:
    """Правило `ignore` для copytree: пропустить одну папку (если задана)."""
    skipped = skip.resolve() if skip else None

    def _ignore(folder: str, names: list[str]) -> set[str]:
        return {name for name in names if _is_same(Path(folder) / name, skipped)}

    return _ignore


def _is_same(path: Path, other: Path | None) -> bool:
    """Путь указывает на ту же папку, что `other`."""
    return other is not None and path.resolve() == other
