"""tests for BaseParser.process file loop."""

from typing import Any
from unittest.mock import MagicMock

from domain.row_item.row_item import RowItem
from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.parser_settings import ParserSettings
from parsers.base_parser.price_files import PriceFiles

_FIRST_FILE = 'brand_kind_cat_tires.xls'
_SECOND_FILE = 'brand_kind_cat_disks.xls'
_FIRST_COUNT = 2
_SECOND_COUNT = 1
_TOTAL_COUNT = 3


class _CannedPriceFiles(PriceFiles):
    """Коллаборатор, отдающий заготовленные строки по файлам без чтения xls."""

    def __init__(self, rows_by_file: dict[str, list[RowItem]]) -> None:
        super().__init__(ParserSettings(), MagicMock())
        self._rows_by_file = rows_by_file
        self.files = list(rows_by_file)

    def raw_parse(self, full_file_xls_path: str) -> list[dict[str, Any]]:
        return [{'file': full_file_xls_path}]

    def map_items(self, raw_rows: list[dict[str, Any]]) -> list[RowItem]:
        mapped_rows: list[RowItem] = []
        for raw in raw_rows:
            mapped_rows.extend(self._rows_by_file[str(raw['file'])])
        return mapped_rows


class _ProcessParser(BaseParser):
    """Парсер с заготовленными файлами; enrich и построчные хуки отключены."""

    def __init__(self, rows_by_file: dict[str, list[RowItem]]) -> None:
        super().__init__(_parse_config())
        self.price_files = _CannedPriceFiles(rows_by_file)

    def enrich(self, row_items: list[RowItem]) -> list[RowItem]:
        return row_items

    def process_parsed_row(self, row_item: RowItem) -> None:
        """File-loop stub: no markup policy."""


def _parse_config() -> MagicMock:
    parse_params = MagicMock(sheet_info='')
    parse_params.supplier.name = 'Тест'
    return MagicMock(parser_params=parse_params, is_enabled=True)


def test_process_without_files_returns_zero() -> None:
    parser = _ProcessParser({})
    parser.price_files.files = None
    assert parser.process() == 0
    assert parser.parsed_items == []


def test_process_sums_rows_from_two_files() -> None:
    first_rows = [RowItem({}) for _ in range(_FIRST_COUNT)]
    second_rows = [RowItem({}) for _ in range(_SECOND_COUNT)]
    parser = _ProcessParser(
        {
            _FIRST_FILE: first_rows,
            _SECOND_FILE: second_rows,
        }
    )

    assert parser.process() == _TOTAL_COUNT
    assert parser.parsed_items == first_rows + second_rows
    assert parser.price_files.type_production == 'disks.xls'


def test_process_accumulates_across_calls() -> None:
    """Повторный process() добавляет строки, а не перезаписывает результат."""
    parser = _ProcessParser({_FIRST_FILE: [RowItem({}), RowItem({})]})
    parser.process()
    parser.process()
    assert len(parser.parsed_items) == 4
