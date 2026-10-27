"""tests for BaseParser.process file loop."""

from typing import Any
from unittest.mock import MagicMock

from domain.row_item.row_item import RowItem
from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.parser_settings import ParserSettings
from parsers.base_parser.price_files import PriceFiles
from parsers.base_parser.row_enricher import RowEnricher
from parsers.base_parser.row_pipeline import RowPipeline

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


class _PassThroughEnricher(RowEnricher):
    """Enrich без разбора строк: тесты файлового цикла не нуждаются в title и производителе."""

    def enrich(self, row_items: list[RowItem]) -> list[RowItem]:
        return row_items


class _NoRowSteps(RowPipeline):
    """File-loop stub: построчные шаги (наценка и т.п.) отключены."""

    def process_row(self, row_item: RowItem) -> None:
        """Ничего не делает."""


def _parser(rows_by_file: dict[str, list[RowItem]]) -> BaseParser:
    """Парсер с заготовленными файлами; enrich и построчные шаги отключены."""
    parser = BaseParser(_parse_config())
    parser.price_files = _CannedPriceFiles(rows_by_file)
    enricher = parser.enricher
    parser.enricher = _PassThroughEnricher(
        parser.settings, enricher.titles, enricher.categories, enricher.manufacturers, parser.stats
    )
    parser.pipeline = _NoRowSteps(None, parser.row_filters, parser.enricher, MagicMock())
    return parser


def _parse_config() -> MagicMock:
    parse_params = MagicMock(sheet_info='')
    parse_params.supplier.name = 'Тест'
    return MagicMock(parser_params=parse_params, is_enabled=True)


def test_process_without_files_returns_zero() -> None:
    parser = _parser({})
    parser.price_files.files = None
    assert parser.process() == 0
    assert parser.parsed_items == []


def test_process_sums_rows_from_two_files() -> None:
    first_rows = [RowItem({}) for _ in range(_FIRST_COUNT)]
    second_rows = [RowItem({}) for _ in range(_SECOND_COUNT)]
    parser = _parser(
        {
            _FIRST_FILE: first_rows,
            _SECOND_FILE: second_rows,
        }
    )

    assert parser.process() == _TOTAL_COUNT
    assert parser.parsed_items == first_rows + second_rows


def test_process_accumulates_across_calls() -> None:
    """Повторный process() добавляет строки, а не перезаписывает результат."""
    parser = _parser({_FIRST_FILE: [RowItem({}), RowItem({})]})
    parser.process()
    parser.process()
    assert len(parser.parsed_items) == 4
