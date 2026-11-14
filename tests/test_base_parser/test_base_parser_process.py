"""tests for BaseParser.process file loop."""

from typing import Any
from unittest.mock import MagicMock

from domain.product_group_result import TireAndDiskResult
from domain.product_groups import ProductGroup
from domain.row_item.row_item import RowItem
from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.file_reader import FileReader
from parsers.base_parser.price_files import PriceFiles
from parsers.base_parser.price_source import FilePricesSource
from parsers.base_parser.row_enricher import RowEnricher
from parsers.base_parser.row_filters import RowFilters
from parsers.base_parser.row_pipeline import RowPipeline
from parsers.base_parser.strategy_hooks import StrategyHooks
from parsers.base_parser.tire_and_disk_handler import TireAndDiskHandler

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


def _parser(rows_by_file: RawRowsByFile) -> BaseParser:
    """Парсер с заготовленными файлами; enrich и построчные шаги отключены."""
    original = BaseParser(_parse_config())
    enricher = original.group_handler.pipeline.enricher
    group = TireAndDiskHandler(
        settings=original.settings,
        stats=original.stats,
        pipeline=RowPipeline(
            StrategyHooks(pipeline=()),
            RowFilters(),
            _PassThroughEnricher(
                original.settings, enricher.titles, enricher.categories, enricher.manufacturers, original.stats
            ),
            MagicMock(),
        ),
    )
    parser = BaseParser(group_handler=group)
    parser.price_files = _CannedPriceFiles(rows_by_file)
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
    assert isinstance(parser._package, TireAndDiskResult)


def test_default_file_reader_uses_parse_config() -> None:
    parse_config = _parse_config()
    title_filter = MagicMock()
    parser = BaseParser(parse_config, title_filter=title_filter)

    assert parser.price_files.routing is parse_config.routing
    file_reader = parser.price_files.file_reader
    assert isinstance(file_reader, FileReader)
    price_source = file_reader._price_source
    assert isinstance(price_source, FilePricesSource)
    assert price_source._config_provider is parse_config.config_provider
    graph = parser.group_handler.pipeline
    assert graph.enricher.titles.title_filter is title_filter


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
