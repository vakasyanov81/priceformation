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
_MSG_PATH = "Ожидается полный путь к файлу"


def load_config(source_raw: str) -> str:
    """Переместить файл настроек в parse_config, заменив существующий."""
    if not source_raw:
        raise ConfigFileNotFoundError(_MSG_PATH)
    source = Path(source_raw)
    dest = _destination(source)
    _ensure_allowed(source)
    _validate_json(source)
    return _move_config(source, dest)


def _destination(source: Path) -> Path:
    name = source.stem + source.suffix.lower()
    return Path(get_parse_paths().user_config_folder) / name


def _ensure_allowed(source: Path) -> None:
    if not _is_allowed_name(source):
        raise InvalidConfigKindError(_MSG_KIND.format(source.name))
    if not source.is_file():
        raise ConfigFileNotFoundError(f"Файл не найден: {source}")


def _is_allowed_name(source: Path) -> bool:
    return source.name == _BLACK_LIST_NAME or source.suffix.lower() in _ALLOWED_SUFFIXES


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
