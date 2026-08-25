"""JSON price reader: list[dict] with string column mapping."""

import json
from pathlib import Path
from typing import Any, cast

from core.exceptions import CoreExceptionError
from parsers.xls_reader import IXlsReader

type JsonRow = dict[str, Any]
type JsonRows = list[JsonRow]
type ColumnMap = dict[str, str]


class JsonPriceNotListError(CoreExceptionError):
    """JSON root is not a list of row objects."""

    def __init__(self) -> None:
        super().__init__("JSON price must be a list of objects")


class JsonPriceReader(IXlsReader):
    """Read a UTF-8 JSON list and rename keys via ParserParams.columns."""

    @classmethod
    def get_instance(cls, file_path: str, reader_params: dict[str, Any]) -> JsonPriceReader:
        if not Path(file_path).exists():
            raise FileNotFoundError
        return cls(file_path, reader_params)

    def __init__(self, file_path: str, reader_params: dict[str, Any]) -> None:
        self._file_path = file_path
        self._columns = columns_from_params(reader_params)

    def parse(self, sheet_indexes: list[int] | None = None) -> JsonRows:
        """JSON has no worksheets; sheet_indexes is ignored."""
        rows = _load_json_rows(self._file_path)
        rename_fields(rows, self._columns)
        return rows


def rename_fields(rows: JsonRows, columns: ColumnMap) -> None:
    """Rename JSON keys to RowItem field names in-place."""
    for row in rows:
        for source_key, target_key in columns.items():
            if source_key in row:
                row[target_key] = row.pop(source_key)


def columns_from_params(reader_params: dict[str, Any]) -> ColumnMap:
    """Keep string-key columns; ignore xls int→name maps."""
    raw_columns = reader_params.get("columns") or {}
    mapped: ColumnMap = {}
    for key, name in raw_columns.items():
        if isinstance(key, str):
            mapped[key] = name
    return mapped


def _load_json_rows(file_path: str) -> JsonRows:
    loaded: Any = json.loads(Path(file_path).read_text(encoding="utf-8"))
    if not isinstance(loaded, list):
        raise JsonPriceNotListError()
    return cast(JsonRows, loaded)
