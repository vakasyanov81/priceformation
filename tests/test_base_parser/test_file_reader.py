"""tests for FileReader.raw_parse: путь файла и вкладки доходят до читателя."""

from types import SimpleNamespace
from typing import Any, ClassVar

from parsers.base_parser.file_reader import FileReader

_PATH = 'prices/vendor.xls'
_START_ROW = 3
_COLUMNS = {0: 'title', 5: 'price'}
_SHEET_INDEXES = (0, 1)


class _RecordingReader:
    """Читатель, запоминающий путь и вкладки, с которыми его создали и вызвали."""

    created: ClassVar[list[_RecordingReader]] = []

    def __init__(self, file_path: str, reader_params: dict[str, Any]) -> None:
        self.file_path = file_path
        self.reader_params = reader_params
        self.parsed_indexes: Any = 'unset'

    @classmethod
    def get_instance(cls, file_path: str, reader_params: dict[str, Any]) -> _RecordingReader:
        instance = cls(file_path, reader_params)
        cls.created.append(instance)
        return instance

    def parse(self, sheet_indexes: Any = None) -> list[dict[str, Any]]:
        self.parsed_indexes = sheet_indexes
        return []


def test_raw_parse_passes_path_and_sheet_indexes() -> None:
    """Путь и вкладки доходят до читателя без подмены на None."""
    _RecordingReader.created.clear()
    reader = FileReader(data_reader=_RecordingReader)
    parser_params = SimpleNamespace(start_row=_START_ROW, columns=_COLUMNS, sheet_indexes=_SHEET_INDEXES)

    reader.raw_parse(_PATH, parser_params)

    instance = _RecordingReader.created[0]
    assert instance.file_path == _PATH
    assert instance.reader_params == {'start_row': _START_ROW - 1, 'columns': _COLUMNS}
    assert instance.parsed_indexes == _SHEET_INDEXES
