"""Схема прайса: чтение шапки файла и заголовки используемых колонок."""

import json
from itertools import islice
from pathlib import Path

from python_calamine import CalamineWorkbook

from parsers.price_schema.header import column_header
from parsers.price_schema.models import Columns, FileHead, PriceSchema, SheetHead, SheetSchema

_HEADER_ROWS_LIMIT = 100
_JSON_SUFFIX = '.json'


def read_file_head(path: Path) -> FileHead:
    """Прочитать шапку файла: json — ключи записей, иначе первые строки каждой вкладки."""
    if path.suffix.lower() == _JSON_SUFFIX:
        return FileHead(json_keys=_json_keys(path))
    book = CalamineWorkbook.from_path(str(path))
    return FileHead(sheets=tuple(_sheet_head(book, name) for name in book.sheet_names))


def build_schema(head: FileHead, *, start_row: int, sheet_indexes: tuple[int, ...], columns: Columns) -> PriceSchema:
    """Схема секции: для каждой вкладки секции — заголовки используемых колонок (последний текст над данными)."""
    if head.json_keys or not head.sheets:
        used = {key for key in columns if isinstance(key, str)}
        return PriceSchema(sheets={}, json_keys=frozenset(used & head.json_keys))
    return PriceSchema(sheets=_sheets_schema(head, start_row, sheet_indexes, columns), json_keys=frozenset())


def _sheets_schema(
    head: FileHead, start_row: int, sheet_indexes: tuple[int, ...], columns: Columns
) -> dict[int, SheetSchema]:
    """Схемы вкладок секции по индексу; индексы за пределами файла пропускаются."""
    mapped = [key for key in columns if isinstance(key, int)]
    zone = max(start_row - 1, 0)
    indexes = sheet_indexes or tuple(range(len(head.sheets)))
    existing = [index for index in indexes if index < len(head.sheets)]
    return {index: _sheet_schema(head.sheets[index], mapped, zone) for index in existing}


def _sheet_head(book: CalamineWorkbook, name: str) -> SheetHead:
    """Первые строки вкладки."""
    rows = islice(book.get_sheet_by_name(name).iter_rows(), _HEADER_ROWS_LIMIT)
    return SheetHead(name, tuple(tuple(row) for row in rows))


def _sheet_schema(sheet: SheetHead, mapped: list[int], zone: int) -> SheetSchema:
    """Название вкладки и заголовки используемых колонок над строкой данных."""
    headers = {column: column_header(sheet.rows[:zone], column) for column in mapped}
    titled = {column: text for column, text in headers.items() if text}
    return SheetSchema(sheet.name, titled)


def _json_keys(path: Path) -> frozenset[str]:
    """Объединение ключей всех записей json-прайса."""
    records = json.loads(path.read_text(encoding='UTF-8'))
    rows = records if isinstance(records, list) else []
    return frozenset(key for row in rows if isinstance(row, dict) for key in row)
