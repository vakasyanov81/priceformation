"""fake xls reader"""

from collections.abc import Sequence
from typing import Any

from parsers.raw_table import RawRow, RawTable
from parsers.xls_reader import IXlsReader


class FakeXlsReader(IXlsReader):
    """fake xls reader"""

    parse_result = None

    @classmethod
    def get_instance(cls, file_path: str, reader_params: dict[str, Any]) -> FakeXlsReader:
        """get instance FakeXlsReader"""
        return FakeXlsReader(file_path, reader_params)

    def __init__(self, file_path: str, reader_params: dict[str, Any]) -> None:
        """init"""
        self.file_path = file_path
        self.reader_params = reader_params
        self.sheet_indexes: Sequence[int] | None = None

    def parse(self, sheet_indexes: Sequence[int] | None = None) -> Any:
        """do parse"""

        self.sheet_indexes = sheet_indexes
        return self.parse_result() if callable(self.parse_result) else self.parse_result

    def raw_tables(self, sheet_indexes: Sequence[int] | None = None) -> list[RawTable]:
        source_rows: list[dict[str, Any]] | None = (
            self.parse_result() if callable(self.parse_result) else self.parse_result
        )
        rows: list[RawRow] = []
        for index, row in enumerate(source_rows or [], start=1):
            rows.append(RawRow(dict(row), index))
        return [RawTable(0, tuple(rows))]
