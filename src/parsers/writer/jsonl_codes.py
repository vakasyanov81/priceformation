"""Кодирование повторяющихся строковых значений jsonl (кроме title)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from parsers.row_item.row_item import RowItem
from parsers.writer.jsonl_codeable import is_codable_value, usable_codes
from parsers.writer.templates.column_helper import ColumnHelper

VALUES_KEY = "values"
_CODE_PREFIX = "@"
_MIN_REPEAT = 2

type JsonlRow = dict[str, Any]
type ValueCodes = dict[str, Any]
type ColumnDefs = list[dict[str, Any]]
type NameToKey = dict[str, str]
type CellToCode = dict[Any, str]


def apply_value_codes(
    rows: list[JsonlRow],
    columns: ColumnDefs,
    name_to_key: NameToKey,
    meta_path: Path,
) -> None:
    """Заменить повторяющиеся строки на @N, если код короче значения."""
    skipped = _title_keys(columns, name_to_key)
    codebook = _assign_codes(rows, skipped, read_value_codes(meta_path))
    _replace_values(rows, skipped, {original: code for code, original in codebook.items()})
    _save_values(meta_path, codebook)


def read_value_codes(meta_path: Path) -> ValueCodes:
    """Словарь @N → исходное значение из result_meta.json."""
    if not meta_path.exists():
        return {}
    loaded = json.loads(meta_path.read_text(encoding="utf-8"))
    raw = loaded.get(VALUES_KEY)
    if isinstance(raw, dict):
        return raw
    return {}


def _title_keys(columns: ColumnDefs, name_to_key: NameToKey) -> set[str]:
    skipped: set[str] = set()
    for column in columns:
        helper = ColumnHelper(column)
        if helper.field != RowItem.title.name:
            continue
        skipped.add(name_to_key[helper.name])
    return skipped


def _count_cells(rows: list[JsonlRow], skipped: set[str]) -> dict[Any, int]:
    counts: dict[Any, int] = {}
    for row in rows:
        for key, cell in row.items():
            if key in skipped or not is_codable_value(cell):
                continue
            counts[cell] = counts.get(cell, 0) + 1
    return counts


def _assign_codes(rows: list[JsonlRow], skipped: set[str], existing: ValueCodes) -> ValueCodes:
    reverse = usable_codes(existing)

    def _register(original: object, count: int) -> None:
        if original in reverse or count < _MIN_REPEAT:
            return
        next_code = f"{_CODE_PREFIX}{_next_index()}"
        if not is_codable_value(original, next_code):
            return
        reverse[original] = next_code

    def _next_index() -> int:
        used = [int(code[1:]) for code in reverse.values()]
        return max(used, default=0) + 1

    for original, count in _count_cells(rows, skipped).items():
        _register(original, count)
    return {code: source for source, code in reverse.items()}


def _replace_values(rows: list[JsonlRow], skipped: set[str], to_code: CellToCode) -> None:
    def _patch(row: JsonlRow) -> None:
        for key, cell in row.items():
            coded = to_code.get(cell)
            if key in skipped or coded is None:
                continue
            row[key] = coded

    for row in rows:
        _patch(row)


def _save_values(meta_path: Path, codebook: ValueCodes) -> None:
    loaded = json.loads(meta_path.read_text(encoding="utf-8"))
    if codebook:
        loaded[VALUES_KEY] = codebook
    else:
        loaded.pop(VALUES_KEY, None)
    meta_path.write_text(json.dumps(loaded, ensure_ascii=False), encoding="utf-8")
