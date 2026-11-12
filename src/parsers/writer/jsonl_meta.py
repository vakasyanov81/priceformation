"""Проверка реестра файлов JSONL v2 до изменения результатов."""

import json
from pathlib import Path
from typing import Any

from domain.exceptions import ConfigValidationError
from parsers.writer.jsonl_schema import IDENTITY_KEYS, valid_envelope, valid_name, valid_schema

RESULT_META_FILE = 'result_meta.json'

type FileSchema = dict[str, Any]
type FileRegistry = dict[str, FileSchema]


def metadata_error(path: Path) -> ConfigValidationError:
    """Несовместимый результат необходимо пересоздать в чистом каталоге."""
    return ConfigValidationError(f'{path}: несовместимые метаданные JSONL; пересоздайте результат в чистом каталоге')


def read_registry(folder: Path) -> FileRegistry:
    """Принять только полный реестр v2, включая записи других запусков."""
    path = folder / RESULT_META_FILE
    if not path.exists():
        return {}
    payload = _load_metadata(path)
    if not valid_envelope(payload):
        raise metadata_error(path)
    registry: FileRegistry = payload['files']
    if not _valid_registry(registry):
        raise metadata_error(path)
    return registry


def check_existing(folder: Path, registry: FileRegistry, planned: FileRegistry) -> None:
    """Принадлежность существующих потоков должна совпадать с новым планом."""
    names = {name.casefold(): name for name in registry}
    for name, schema in planned.items():
        if names.get(name.casefold(), name) != name:
            raise metadata_error(folder / name)
        _check_file(folder / name, registry.get(name), schema)


def _check_file(path: Path, previous: FileSchema | None, planned: FileSchema) -> None:
    if previous is None:
        if path.exists():
            raise metadata_error(path)
    elif any(previous[key] != planned[key] for key in IDENTITY_KEYS):
        raise metadata_error(path)


def _load_metadata(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (UnicodeError, ValueError) as exc:
        raise metadata_error(path) from exc


def _valid_registry(registry: FileRegistry) -> bool:
    for name, schema in registry.items():
        if not valid_name(name) or not valid_schema(schema):
            return False
    unique_names = {entry.casefold() for entry in registry}
    return len(unique_names) == len(registry)
