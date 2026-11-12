"""Кодирование повторяющихся строковых значений jsonl (кроме title)."""

from __future__ import annotations

from typing import Any

from parsers.writer.jsonl_codeable import is_codable_value

_CODE_PREFIX = '@'
_MIN_REPEAT = 2

type JsonlRow = dict[str, Any]
type ValueCodes = dict[str, Any]
type CellToCode = dict[Any, str]


def apply_value_codes(rows: list[JsonlRow], skipped: set[str]) -> ValueCodes:
    """Коды локальны потоку; поля названия передаёт преобразователь группы."""
    codebook = _assign_codes(rows, skipped)
    _replace_values(rows, skipped, {original: code for code, original in codebook.items()})
    return codebook


def _count_cells(rows: list[JsonlRow], skipped: set[str]) -> dict[Any, int]:
    counts: dict[Any, int] = {}
    for row in rows:
        for key, cell in row.items():
            if key in skipped or not is_codable_value(cell):
                continue
            counts[cell] = counts.get(cell, 0) + 1
    return counts


def _assign_codes(rows: list[JsonlRow], skipped: set[str]) -> ValueCodes:
    reverse: CellToCode = {}
    reserved = {cell for row in rows for cell in row.values() if isinstance(cell, str)}

    def _register(original: object, count: int) -> None:
        if original in reverse or count < _MIN_REPEAT:
            return
        next_code = _next_code(set(reverse.values()), reserved)
        if not is_codable_value(original, next_code):
            return
        reverse[original] = next_code

    for counted in _count_cells(rows, skipped).items():
        _register(*counted)
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


def _next_code(used: set[str], reserved: set[str]) -> str:
    indexes = (int(code[1:]) for code in used)
    index = max(indexes, default=0) + 1
    while f'{_CODE_PREFIX}{index}' in reserved:
        index += 1
    return f'{_CODE_PREFIX}{index}'
