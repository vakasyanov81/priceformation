"""От входного XLSX до независимых выходных книг или листов двух моделей."""

from collections.abc import Iterator
from contextlib import ExitStack, closing, contextmanager
from pathlib import Path

import openpyxl
import pytest
from openpyxl.workbook.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet

from domain.product_groups import ProductGroup
from integration_tests.group_xlsx_examples import DATE, OTHER, TIRES, output_sources, output_template
from parsers.writer.templates.group_output import OutputMode
from tests.group_output_examples import group_writer

_EMPTY_CHOICES = ((), (TIRES,), (OTHER,), (TIRES, OTHER))
_FIRST_CELL = 'A2'


@pytest.fixture(params=list(OutputMode))
def output_mode(request: pytest.FixtureRequest) -> OutputMode:
    return OutputMode(request.param)


@pytest.fixture(params=_EMPTY_CHOICES)
def empty_groups(request: pytest.FixtureRequest) -> frozenset[ProductGroup]:
    return frozenset(request.param)


@contextmanager
def _open_books(paths: list[str]) -> Iterator[list[Workbook]]:
    """Закрыть все открытые книги, в том числе при ошибке открытия следующей."""
    with ExitStack() as stack:
        books = []
        for path in paths:
            book = openpyxl.load_workbook(path)
            stack.callback(book.close)
            books.append(book)
        yield books


@pytest.fixture
def output_sheets(
    tmp_path: Path, output_mode: OutputMode, empty_groups: frozenset[ProductGroup]
) -> Iterator[dict[ProductGroup, Worksheet]]:
    """Каждая проверка открывает сохранённые книги и закрывает их после чтения."""
    paths = group_writer(tmp_path / 'result').write(
        [output_template(output_mode)], output_sources(tmp_path / 'input.xlsx', empty_groups), current_date=DATE
    )
    with _open_books(paths) as books:
        tire_sheet = books[0]['Шины']
        other_sheet = books[-1]['Тестовая модель']
        yield {TIRES: tire_sheet, OTHER: other_sheet}


def test_output_book_and_sheet_names(tmp_path: Path, output_mode: OutputMode) -> None:
    """Возвращённые пути совпадают с файлами, лишних листов и книг нет."""
    paths = group_writer(tmp_path / 'result').write(
        [output_template(output_mode)], output_sources(tmp_path / 'input.xlsx'), current_date=DATE
    )
    expected = {f'tires_{DATE}.xlsx': ['Шины'], f'other_{DATE}.xlsx': ['Тестовая модель']}
    if output_mode is OutputMode.WORKBOOK_SHEETS:
        expected = {f'all_{DATE}.xlsx': ['Шины', 'Тестовая модель']}
    assert [Path(path).name for path in paths] == list(expected)
    written = (tmp_path / 'result').iterdir()
    assert sorted(path.name for path in written) == sorted(expected)
    for path in paths:
        with closing(openpyxl.load_workbook(path)) as book:
            assert book.sheetnames == expected[Path(path).name]


def test_group_values_and_empty_headers(
    output_sheets: dict[ProductGroup, Worksheet], empty_groups: frozenset[ProductGroup]
) -> None:
    """Фильтры локальны группе; выбранная пустая группа сохраняет свой заголовок."""
    tire_values: list[tuple[str | float, ...]] = [('Название', 'Цена')]
    if TIRES not in empty_groups:
        tire_values.extend([('SAME', 1250.5), ('SAME', 1250.5)])
    other_values = [('Метка',)]
    if OTHER not in empty_groups:
        other_values.append(('same',))
    assert list(output_sheets[TIRES].values) == tire_values
    assert list(output_sheets[OTHER].values) == other_values


def test_group_formats_remain_independent(
    output_sheets: dict[ProductGroup, Worksheet], empty_groups: frozenset[ProductGroup]
) -> None:
    """Числовой формат и заливка одной модели не переходят на другую."""
    tires = output_sheets[TIRES]
    other = output_sheets[OTHER]
    if TIRES not in empty_groups:
        assert tires[_FIRST_CELL].number_format == '@'
        assert tires['B2'].number_format == '#,##0.00'
        assert tires[_FIRST_CELL].fill.fgColor.rgb == 'FF00FF00'
    if OTHER not in empty_groups:
        assert other[_FIRST_CELL].number_format == '@'
        assert other[_FIRST_CELL].fill.fill_type is None
