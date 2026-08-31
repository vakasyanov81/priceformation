"""Загрузка файлов настроек в parse_config."""

import json
import shutil
from pathlib import Path

from core.parse_paths import get_parse_paths
from parsers.load_config_errors import (
    ConfigFileNotFoundError,
    InvalidConfigJsonError,
    InvalidConfigKindError,
)

_BLACK_LIST_NAME = "black_list"
_JSON_SUFFIX = ".json"
_XLSX_SUFFIX = ".xlsx"
_ALLOWED_SUFFIXES = frozenset((_JSON_SUFFIX, _XLSX_SUFFIX))
_MSG_KIND = "Недопустимый файл {0!r}. Допустимы: *.json, *.xlsx, black_list"
_MSG_JSON = "Файл не является JSON: {0}"
_MSG_PATH = "Ожидается полный путь к файлу или папке"
_MSG_EMPTY = "В папке нет файлов настроек: {0}"


def load_config(source_raw: str) -> list[str]:
    """Переместить файл или файлы из папки в parse_config, заменив существующие."""
    sources = _resolve_sources(source_raw)
    for source in sources:
        _ensure_allowed(source)
        _validate_json(source)
    return [_move_config(config_file, _destination(config_file)) for config_file in sources]


def _resolve_sources(source_raw: str) -> list[Path]:
    if not source_raw:
        raise ConfigFileNotFoundError(_MSG_PATH)
    source = Path(source_raw)
    if source.is_dir():
        return _files_in_folder(source)
    if source.exists():
        return [source]
    raise ConfigFileNotFoundError(f"Файл или папка не найдены: {source}")


def _files_in_folder(folder: Path) -> list[Path]:
    sources = sorted(source for source in folder.iterdir() if source.is_file())
    if not sources:
        raise ConfigFileNotFoundError(_MSG_EMPTY.format(folder))
    return sources


def _destination(source: Path) -> Path:
    name = source.stem + source.suffix.lower()
    return Path(get_parse_paths().user_config_folder) / name


def _ensure_allowed(source: Path) -> None:
    allowed_name = source.name == _BLACK_LIST_NAME or source.suffix.lower() in _ALLOWED_SUFFIXES
    if not allowed_name:
        raise InvalidConfigKindError(_MSG_KIND.format(source.name))


def _validate_json(source: Path) -> None:
    if source.suffix.lower() != _JSON_SUFFIX:
        return
    try:
        json.loads(source.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise InvalidConfigJsonError(_MSG_JSON.format(exc)) from exc


def _move_config(source: Path, dest: Path) -> str:
    if source.resolve() == dest.resolve():
        return str(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.unlink(missing_ok=True)
    shutil.move(source, dest)
    return str(dest)
