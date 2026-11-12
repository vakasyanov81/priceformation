"""Изоляция моделей одного поставщика от чтения колонок до пакетов результата."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from openpyxl import Workbook

from domain.product_group_handler import OutputFields, ProductGroupHandler
from domain.product_group_result import ProductGroupResult, ProductPosition, TireAndDiskResult
from domain.product_groups import DuplicateGroupKey, ProductGroup
from domain.row_item.row_item import RowItem
from integration_tests.product_group_examples import OtherStrategy, TireStrategy
from parsers.base_parser.base_parser_config import ParseParamsSupplier, ParserParams
from parsers.base_parser.file_reader import FileReader
from parsers.base_parser.price_files import PriceFiles
from parsers.common_price.exclude_doubles import exclude_doubles
from services.parse_result import ParseResult
from tests.test_domain.group_handler_examples import TestPosition

_TITLE = 'title'
_SAME = 'same'
_UPPER_SAME = 'SAME'


def _read_group[TPosition: ProductPosition](
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


def _supplier_price(path: Path) -> None:
    workbook = Workbook()
    sheet = workbook.active
    assert sheet is not None
    sheet.append(['Шинное название', 'Произвольная метка'])
    sheet.append([_SAME, ' SAME '])
    sheet.append([_SAME, _SAME])
    sheet.append(['different', ' OTHER '])
    workbook.save(path)
    workbook.close()


@pytest.fixture(params=[False, True])
def supplier_groups(tmp_path: Path, request: pytest.FixtureRequest) -> ParseResult:
    """Порядок обработки групп одного поставщика не влияет на результат."""
    path = tmp_path / 'supplier.xlsx'
    _supplier_price(path)
    tire_package: ProductGroupResult[RowItem]
    other_package: ProductGroupResult[TestPosition]
    if request.param:
        other_package = _read_group(path, OtherStrategy(), {1: 'label'})
        tire_package = _read_group(path, TireStrategy(), {0: _TITLE})
    else:
        tire_package = _read_group(path, TireStrategy(), {0: _TITLE})
        other_package = _read_group(path, OtherStrategy(), {1: 'label'})
    parse_result = ParseResult()
    for package in (other_package, tire_package) if request.param else (tire_package, other_package):
        parse_result.add_package(package)
    return parse_result


def test_supplier_columns_and_models(supplier_groups: ParseResult) -> None:
    """Карты колонок и стратегии не переносят поля в соседнюю модель."""
    assert [row.identity.title for row in supplier_groups.tire_and_disk_items] == [
        'DIFFERENT',
        _UPPER_SAME,
        _UPPER_SAME,
    ]
    other_positions = supplier_groups.groups[ProductGroup.BATTERIES].positions
    assert other_positions == (TestPosition(_SAME), TestPosition('other'))
    assert supplier_groups.total_statistics().item_count == 5


def test_supplier_duplicate_rules(supplier_groups: ParseResult) -> None:
    """Шинные дубли сохраняются с признаками, тестовые повторы удаляются отдельно."""
    rows = supplier_groups.tire_and_disk_items
    assert sum(bool(row.duplicate.is_double) for row in rows) == 1
    assert sum(bool(row.duplicate.double_candidate) for row in rows) == 1
    assert len(exclude_doubles(rows)) == 2
    assert len(supplier_groups.groups[ProductGroup.BATTERIES].positions) == 2


def test_supplier_output_and_duplicate_keys(supplier_groups: ParseResult) -> None:
    """Скалярный вывод и внешние адреса дублей сохраняют границу моделей."""
    tire_package = TireAndDiskResult(tuple(supplier_groups.tire_and_disk_items))
    output: tuple[OutputFields, ...] = (
        {_TITLE: 'DIFFERENT', 'price': 0},
        {_TITLE: _UPPER_SAME, 'price': 0},
        {_TITLE: _UPPER_SAME, 'price': 0},
    )
    assert TireStrategy().prepare_output(tire_package) == output
    tire_key = DuplicateGroupKey(ProductGroup.TIRE_AND_DISK, 1)
    other_key = DuplicateGroupKey(ProductGroup.BATTERIES, 1)
    assert len({tire_key: tire_package, other_key: supplier_groups.groups[ProductGroup.BATTERIES]}) == 2
