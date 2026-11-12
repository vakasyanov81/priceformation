"""Тестовые стратегии двух моделей; не регистрируются в приложении."""

from collections.abc import Sequence
from dataclasses import replace
from pathlib import Path
from unittest.mock import MagicMock

from openpyxl import Workbook

from domain.product_group_handler import ProductGroupHandler
from domain.product_group_result import ProductGroupResult, ProductPosition, TireAndDiskResult
from domain.row_item.row_item import RowItem
from parsers.base_parser.base_parser_config import ParseParamsSupplier, ParserParams
from parsers.base_parser.file_reader import FileReader
from parsers.base_parser.price_files import PriceFiles
from parsers.common_price.grouper import CommonPriceGrouper
from tests.test_domain.group_handler_examples import (
    OtherHandlerExample,
    TestGroupResult,
    TestPosition,
    TireHandlerExample,
)


class TireStrategy(TireHandlerExample):
    """Шинная обработка сохраняет предложения и отмечает дубли рабочим группировщиком."""

    def process(self, positions: Sequence[RowItem]) -> TireAndDiskResult:
        for position in positions:
            title = position.identity.title or ''
            position.identity = replace(position.identity, title=title.upper(), model=title)
        return TireAndDiskResult(tuple(positions))

    def group(self, package: ProductGroupResult[RowItem]) -> TireAndDiskResult:
        grouped = CommonPriceGrouper(list(package.positions)).group_by_params().get_row_items()
        return TireAndDiskResult(tuple(grouped))


class OtherStrategy(OtherHandlerExample):
    """Произвольное правило второй модели: нормализация и удаление повторных меток."""

    def process(self, positions: Sequence[TestPosition]) -> TestGroupResult:
        normalized = (TestPosition(position.label.strip().lower()) for position in positions)
        return TestGroupResult(tuple(normalized))

    def group(self, package: ProductGroupResult[TestPosition]) -> TestGroupResult:
        return TestGroupResult(tuple(dict.fromkeys(package.positions)))


def read_group[TPosition: ProductPosition](
    path: Path,
    group_handler: ProductGroupHandler[TPosition],
    columns: dict[int, str],
) -> ProductGroupResult[TPosition]:
    """Общая механика читает одну таблицу поставщика с разными картами полей."""
    parser_params = ParserParams(
        supplier=ParseParamsSupplier('demo', 'Поставщик', group_handler.product_group.value),
        start_row=2,
        sheet_info='',
        columns=columns,
        stop_words=(),
        file_templates=('*.xlsx',),
        sheet_indexes=(0,),
    )
    files = PriceFiles(parser_params, FileReader(price_source=MagicMock()))
    positions = files.read_positions([str(path)], group_handler.create_position)
    return group_handler.group(group_handler.process(positions))


def supplier_price(path: Path) -> None:
    workbook = Workbook()
    sheet = workbook.active
    assert sheet is not None
    sheet.append(['Шинное название', 'Произвольная метка', 'Цена'])
    sheet.append(['same', ' SAME ', 1250.5])
    sheet.append(['same', 'same', 1250.5])
    sheet.append(['different', ' OTHER ', 2499])
    workbook.save(path)
    workbook.close()
