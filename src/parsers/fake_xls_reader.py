"""fake xls reader"""

from typing import Any

from parsers.xls_reader import IXlsReader


class FakeXlsReader(IXlsReader):
    """fake xls reader"""

    parse_result = None

    @classmethod
    def get_instance(cls, file_path: str, *_args: Any) -> "FakeXlsReader":
        """get instance FakeXlsReader"""
        return FakeXlsReader(file_path)

    def __init__(self, file_path: str) -> None:
        """init"""
        self.file_path = file_path
        self.sheet_indexes: list[int] | None = None

    def parse(self, sheet_indexes: list[int] | None = None) -> Any:
        """do parse"""

        self.sheet_indexes = sheet_indexes
        return self.parse_result() if callable(self.parse_result) else self.parse_result
