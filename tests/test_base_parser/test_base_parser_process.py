"""tests for BaseParser.process file loop."""

from typing import Any
from unittest.mock import MagicMock

from domain.product_groups import ProductGroup
from domain.row_item.row_item import RowItem
from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.price_files import PriceFiles
from parsers.base_parser.row_enricher import RowEnricher
from parsers.base_parser.row_pipeline import RowPipeline

type RawRowsByFile = dict[str, list[dict[str, Any]]]

_FIRST_FILE = 'brand_kind_cat_tires.xls'
_SECOND_FILE = 'brand_kind_cat_disks.xls'
_FIRST_COUNT = 2
_SECOND_COUNT = 1
_TOTAL_COUNT = 3


class _CannedPriceFiles(PriceFiles):
    """Коллаборатор, отдающий заготовленные строки по файлам без чтения xls."""

    def __init__(self, rows_by_file: RawRowsByFile) -> None:
        super().__init__(MagicMock(), MagicMock())
        self._rows_by_file = rows_by_file
        self.files = list(rows_by_file)

    def raw_parse(self, full_file_xls_path: str) -> list[dict[str, Any]]:
        return self._rows_by_file[full_file_xls_path]


class _PassThroughEnricher(RowEnricher):
    """Enrich без разбора строк: тесты файлового цикла не нуждаются в title и производителе."""

    def enrich(self, row_items: list[RowItem]) -> list[RowItem]:
        return row_items


class _NoRowSteps(RowPipeline):
    """File-loop stub: построчные шаги (наценка и т.п.) отключены."""

    def process_row(self, row_item: RowItem) -> None:
        """Ничего не делает."""


def _parser(rows_by_file: RawRowsByFile) -> BaseParser:
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


def _row() -> dict[str, Any]:
    """Строка, которая переживает финальный отсев обработчика группы."""
    return {'title': 'Шина', 'price_opt': 100, 'rest_count': 4}


def test_process_without_files_returns_zero() -> None:
    parser = _parser({})
    parser.price_files.files = None
    assert parser.process() == 0
    assert parser.parsed_items == []


def test_diagnostic_group_matches_handler() -> None:
    """Контекст ошибки берётся из обработчика той же модели, что и пакет результата."""
    parser = _parser({})
    assert parser.product_group is ProductGroup.TIRE_AND_DISK


def test_process_sums_rows_from_two_files() -> None:
    first_rows: list[dict[str, Any]] = [_row() for _ in range(_FIRST_COUNT)]
    second_rows: list[dict[str, Any]] = [_row() for _ in range(_SECOND_COUNT)]
    parser = _parser(
        {
            _FIRST_FILE: first_rows,
            _SECOND_FILE: second_rows,
        }
    )

    assert parser.process() == _TOTAL_COUNT
    assert len(parser.parsed_items) == _TOTAL_COUNT
    assert all(isinstance(row, RowItem) for row in parser.parsed_items)


def test_process_accumulates_across_calls() -> None:
    """Повторный process() добавляет строки, а не перезаписывает результат."""
    parser = _parser({_FIRST_FILE: [_row(), _row()]})
    parser.process()
    parser.process()
    assert len(parser.parsed_items) == 4
