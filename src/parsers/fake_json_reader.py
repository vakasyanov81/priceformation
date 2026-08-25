"""In-memory JSON price reader for parser tests (no disk)."""

from typing import Any, ClassVar

from parsers.json_reader import JsonRows, columns_from_params, rename_fields
from parsers.xls_reader import IXlsReader


class FakeJsonPriceReader(IXlsReader):
    """Apply columns mapping to class-level rows, like JsonPriceReader without I/O."""

    raw_rows: ClassVar[JsonRows] = []

    @classmethod
    def get_instance(cls, file_path: str, reader_params: dict[str, Any]) -> FakeJsonPriceReader:
        return cls(file_path, reader_params)

    def __init__(self, file_path: str, reader_params: dict[str, Any]) -> None:
        self.file_path = file_path
        self._columns = columns_from_params(reader_params)

    def parse(self, sheet_indexes: list[int] | None = None) -> JsonRows:
        """JSON has no worksheets; sheet_indexes is ignored."""
        rows = [dict(row) for row in self.raw_rows]
        rename_fields(rows, self._columns)
        return rows
