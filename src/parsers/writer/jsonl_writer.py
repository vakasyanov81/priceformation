"""JSONL-результат по шаблону записи (те же колонки, что у xlsx)."""

from __future__ import annotations

import datetime
import json
from pathlib import Path
from typing import Any

from parsers.writer.jsonl_codes import VALUES_KEY, apply_value_codes, read_value_codes
from parsers.writer.templates.column_helper import ColumnHelper
from parsers.writer.templates.iwrite_template import IWriteTemplate
from parsers.writer.xls_writer import PriceRow, get_value, make_exclude

RESULT_META_FILE = "result_meta.json"
_SEPARATORS = (",", ":")

type JsonlColumns = list[dict[str, Any]]
type NameToKey = dict[str, str]
type KeyToName = dict[str, str]


def write_template_jsonl(
    rows: list[PriceRow],
    template: type[IWriteTemplate],
    result_folder: str,
) -> str:
    """Записать позиции в .jsonl и вернуть абсолютный путь."""
    instance = template()
    folder = Path(result_folder)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / _jsonl_file_name(instance)
    _write_jsonl(path, make_exclude(rows, instance.exclude()), instance)
    return str(path.resolve())


def _jsonl_file_name(template: IWriteTemplate) -> str:
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    xlsx_name = template.get_file_name().format(now=current_date)
    return Path(xlsx_name).with_suffix(".jsonl").name


def _write_jsonl(path: Path, rows: list[PriceRow], template: IWriteTemplate) -> None:
    columns = [column for column in template.columns() if not ColumnHelper(column).skip]
    keys = _extend_meta(path.parent, columns)
    compact = [_compact_row(product, columns, keys) for product in rows]
    apply_value_codes(compact, columns, keys, path.parent / RESULT_META_FILE)
    with path.open("w", encoding="utf-8") as stream:
        for packed in compact:
            stream.write(json.dumps(packed, ensure_ascii=False, default=str, separators=_SEPARATORS))
            stream.write("\n")


def _extend_meta(folder: Path, columns: JsonlColumns) -> NameToKey:
    """Дописать колонки в result_meta.json, вернуть имя колонки → ключ."""
    by_name = {name: key for key, name in _read_meta(folder).items()}
    _assign_keys(by_name, columns)
    payload: dict[str, Any] = {key: name for name, key in by_name.items()}
    codebook = read_value_codes(folder / RESULT_META_FILE)
    if codebook:
        payload[VALUES_KEY] = codebook
    (folder / RESULT_META_FILE).write_text(
        json.dumps(payload, ensure_ascii=False),
        encoding="utf-8",
    )
    return by_name


def _assign_keys(by_name: NameToKey, columns: JsonlColumns) -> None:
    used = [int(key) for key in by_name.values()]
    next_index = max(used, default=0) + 1
    for column in columns:
        name = ColumnHelper(column).name
        if name in by_name:
            continue
        by_name[name] = str(next_index)
        next_index += 1


def _read_meta(folder: Path) -> KeyToName:
    path = folder / RESULT_META_FILE
    if not path.exists():
        return {}
    loaded = json.loads(path.read_text(encoding="utf-8"))
    columns: KeyToName = {}
    for key, column_name in loaded.items():
        if not str(key).isdigit():
            continue
        columns[str(key)] = str(column_name)
    return columns


def _compact_row(
    product: PriceRow,
    columns: JsonlColumns,
    name_to_key: NameToKey,
) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for column in columns:
        cell = get_value(column, product)
        if cell is None:
            continue
        payload[name_to_key[ColumnHelper(column).name]] = cell
    return payload
