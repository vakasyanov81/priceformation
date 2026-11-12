"""Публикация потоков с проверкой реестра и восстановлением при ошибке."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from parsers.writer.jsonl_meta import RESULT_META_FILE, FileRegistry, check_existing, read_registry
from parsers.writer.jsonl_schema import META_VERSION


def publish_jsonl(folder: Path, streams: dict[str, str], schemas: FileRegistry) -> list[str]:
    """Проверить все старые схемы, подготовить файлы и заменить реестр последним."""
    if not streams:
        return []
    registry = read_registry(folder)
    check_existing(folder, registry, schemas)
    registry.update(schemas)
    folder.mkdir(parents=True, exist_ok=True)
    payloads = {
        **streams,
        RESULT_META_FILE: json.dumps({'version': META_VERSION, 'files': registry}, ensure_ascii=False),
    }
    _replace_files(folder, payloads)
    return [str((folder / name).resolve()) for name in streams]


def _replace_files(folder: Path, payloads: dict[str, str]) -> None:
    previous = {name: _read_previous(folder / name) for name in payloads}
    replaced: list[str] = []
    with TemporaryDirectory(dir=folder) as staging:
        for name, payload in payloads.items():
            Path(staging, name).write_text(payload, encoding='utf-8')
        try:
            for name in payloads:
                Path(staging, name).replace(folder / name)
                replaced.append(name)
        except OSError:
            _restore_files(folder, {entry: previous[entry] for entry in reversed(replaced)})
            raise


def _read_previous(path: Path) -> bytes | None:
    return path.read_bytes() if path.exists() else None


def _restore_files(folder: Path, previous: dict[str, bytes | None]) -> None:
    for name, original in previous.items():
        path = folder / name
        if original is None:
            path.unlink()
        else:
            path.write_bytes(original)
