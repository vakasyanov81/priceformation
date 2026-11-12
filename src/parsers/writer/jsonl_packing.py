"""Компактная сериализация одного потока без состояния соседних файлов."""

import json
from typing import Any

from parsers.writer.jsonl_codes import apply_value_codes
from parsers.writer.jsonl_meta import FileSchema
from parsers.writer.row_style import PriceRow
from parsers.writer.templates.column_helper import ColumnHelper
from parsers.writer.templates.group_output import WriteColumns
from parsers.writer.xls_writer import cell_value, has_value

_SEPARATORS = (',', ':')

type JsonlColumns = list[ColumnHelper]
type NameToKey = dict[str, str]
type PackedFile = tuple[str, FileSchema]


def pack_rows(rows: list[PriceRow], definitions: WriteColumns, title_fields: frozenset[str]) -> PackedFile:
    """Выдать строки, схему и коды одного файла с нумерацией от единицы."""
    columns = [column for column in map(ColumnHelper, definitions) if not column.skip]
    keys = _column_keys(columns)
    compact = [_compact_row(row, columns, keys) for row in rows]
    schema = _schema(compact, columns, keys, title_fields)
    return ''.join(map(_serialize_row, compact)), schema


def _column_keys(columns: JsonlColumns) -> NameToKey:
    numbered = enumerate(columns, start=1)
    return {column.name: str(index) for index, column in numbered}


def _schema(rows: list[PriceRow], columns: JsonlColumns, keys: NameToKey, title_fields: frozenset[str]) -> FileSchema:
    skipped = {keys[column.name] for column in columns if column.field in title_fields}
    codes = apply_value_codes(rows, skipped)
    return {'columns': {key: name for name, key in keys.items()}, 'value_codes': codes}


def _serialize_row(row: PriceRow) -> str:
    packed = json.dumps(row, ensure_ascii=False, default=str, separators=_SEPARATORS)
    return f'{packed}\n'


def _compact_row(product: PriceRow, columns: JsonlColumns, keys: NameToKey) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for column in columns:
        cell = cell_value(column, product)
        if has_value(cell):
            payload[keys[column.name]] = cell
    return payload
