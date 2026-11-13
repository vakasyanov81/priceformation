"""Контракт сохранённых XLSX: значения, типы, оформление и независимость листов."""

from pathlib import Path
from unittest.mock import patch

import openpyxl
import pytest
from openpyxl.worksheet.worksheet import Worksheet

from parsers.writer.errors import WorkbookNotInitializedError, WorksheetNotInitializedError
from parsers.writer.xlsxwriter_adapter import XlsxWriterAdapter

_FILE_NAME = 'prices.xlsx'
_COLOR = '#12ab34'
_SHORT_VALUES = [
    ('x', 5),
    ('', 4),
    (None, 4),
    (0, 4),
]


def _write_example(driver: XlsxWriterAdapter, folder: Path) -> Path:
    """Шапка, легенда, значения разных типов и второй лист с другим форматом."""
    book = driver.init_workbook(str(folder), _FILE_NAME)
    assert driver.init_workbook(str(folder), _FILE_NAME) is book
    _write_tires(driver)
    _write_other(driver)
    driver.add_sheet('Пустой')
    driver.save()
    return folder / _FILE_NAME


def _write_tires(driver: XlsxWriterAdapter) -> None:
    """Легенда и шапка с отступом, отдельные форматы для текста и чисел."""
    driver.add_sheet('Шины')
    driver.set_column_format({1: '@', 2: '#,##0.00'})
    driver.write(0, 0, None, _color=_COLOR)
    driver.write(0, 1, 'Легенда')
    driver.write_head(['Артикул', 'Цена', 'Ссылка', 'Пусто', 'Наличие'], 2)
    _write_tire_values(driver)


def _write_tire_values(driver: XlsxWriterAdapter) -> None:
    """Текст с нулями, числа, ссылка, флаг и формула сохраняют свои типы."""
    driver.write(3, 0, '001234', _color=_COLOR)
    driver.write(3, 1, 1234.5, _color=_COLOR)
    driver.write(3, 2, 'https://example.com')
    driver.write(3, 4, True)
    driver.write(4, 1, '=1+2')


def _write_other(driver: XlsxWriterAdapter) -> None:
    """Второй лист не наследует форматы первого."""
    driver.add_sheet('Другие')
    driver.write_head(['Шапка'])
    driver.write(1, 0, 'Текст', style=True)
    driver.write(2, 0, 'Коротко')


def test_saved_values_styles_and_widths(tmp_path: Path) -> None:
    """Проверить результат через независимую библиотеку чтения XLSX."""
    book = openpyxl.load_workbook(_write_example(XlsxWriterAdapter(), tmp_path))
    try:
        assert book.sheetnames == ['Шины', 'Другие', 'Пустой']
        _assert_tire_values(book['Шины'])
        _assert_tire_styles(book['Шины'])
        _assert_other_sheet(book['Другие'])
        assert list(book['Пустой'].values) == []
    finally:
        book.close()


def _assert_tire_values(sheet: Worksheet) -> None:
    """Легенда, пустая строка и шапка не сдвигают данные."""
    assert list(sheet.values) == [
        (None, 'Легенда', None, None, None),
        (None, None, None, None, None),
        ('Артикул', 'Цена', 'Ссылка', 'Пусто', 'Наличие'),
        ('001234', 1234.5, 'https://example.com', None, True),
        (None, '=1+2', None, None, None),
    ]
    cell_types = [sheet[cell].data_type for cell in ('A4', 'B4', 'C4', 'E4', 'B5')]
    assert cell_types == ['s', 'n', 's', 'b', 'f']
    assert sheet['C4'].hyperlink is None


def _assert_tire_styles(sheet: Worksheet) -> None:
    """Заливка не теряет числовой формат, ширина учитывает шапку и значения."""
    assert all(cell.font.bold for cell in sheet[3])
    for address in ('A1', 'A4', 'B4'):
        assert sheet[address].fill.patternType == 'solid'
        assert sheet[address].fill.fgColor.rgb == 'FF12AB34'
    assert sheet['A4'].number_format == '@'
    assert sheet['B4'].number_format == '#,##0.00'
    assert sheet['C4'].fill.patternType is None
    expected_widths = {'A': 11, 'B': 11, 'C': 23, 'D': 9, 'E': 11}
    assert {column: dim.width for column, dim in sheet.column_dimensions.items()} == expected_widths


def _assert_other_sheet(sheet: Worksheet) -> None:
    """Форматы колонок и заливки не переходят на следующий лист."""
    assert list(sheet.values) == [('Шапка',), ('Текст',), ('Коротко',)]
    assert sheet['A1'].font.bold is True
    assert sheet['A2'].font.bold is True
    assert sheet['A3'].font.bold is False
    assert sheet['A2'].number_format == 'General'
    assert sheet['A2'].fill.patternType is None
    assert sheet.column_dimensions['A'].width == 11


@pytest.mark.parametrize('operation', ['add_sheet', 'save'])
def test_operations_require_workbook(operation: str) -> None:
    """Ошибки незапущенной записи сохраняют прежний контракт."""
    driver = XlsxWriterAdapter()
    args = ['Шины'] if operation == 'add_sheet' else []
    with pytest.raises(WorkbookNotInitializedError, match=r'^workbook is not initialized$'):
        getattr(driver, operation)(*args)


@pytest.mark.parametrize(
    'operation, args',
    [('write', (0, 0, 'x')), ('set_column_format', ({1: '@'},))],
)
def test_operations_require_sheet(operation: str, args: tuple[object, ...]) -> None:
    """Нельзя записать ячейки или форматы до выбора листа."""
    with pytest.raises(WorksheetNotInitializedError, match=r'^worksheet is not initialized$'):
        getattr(XlsxWriterAdapter(), operation)(*args)


def test_save_requires_sheet(tmp_path: Path) -> None:
    driver = XlsxWriterAdapter()
    book = driver.init_workbook(str(tmp_path), _FILE_NAME)
    with pytest.raises(WorkbookNotInitializedError, match=r'^workbook is not initialized$'):
        driver.save()
    book.close()


def test_formats_are_reused_for_repeated_cells(tmp_path: Path) -> None:
    """Числовой формат с заливкой создаётся один раз на книгу."""
    driver = XlsxWriterAdapter()
    book = driver.init_workbook(str(tmp_path), _FILE_NAME)
    driver.add_sheet('Шины')
    with patch.object(book, 'add_format', wraps=book.add_format) as add_format:
        driver.write(0, 0, 'one', _color=_COLOR)
        driver.write(1, 0, 'two', _color=_COLOR)
        assert add_format.call_count == 2  # Заливка ячейки и обычный формат колонки.
    driver.save()


def test_out_of_bounds_cell_is_reported(tmp_path: Path) -> None:
    """Отрицательный индекс не приводит к молчаливой потере данных."""
    driver = XlsxWriterAdapter()
    driver.init_workbook(str(tmp_path), _FILE_NAME)
    driver.add_sheet('Шины')
    with pytest.raises(ValueError, match='Не удалось записать ячейку'):
        driver.write(-1, 0, 'Позиция')
    driver.save()


@pytest.mark.parametrize(
    'operation, args',
    [('write', (0, 0, 'x')), ('set_column_format', ({1: '@'},))],
)
def test_operations_require_sheet_after_workbook_init(tmp_path: Path, operation: str, args: tuple[object, ...]) -> None:
    """Открытая книга без листа сохраняет доменную ошибку операции."""
    driver = XlsxWriterAdapter()
    book = driver.init_workbook(str(tmp_path), _FILE_NAME)
    try:
        with pytest.raises(WorksheetNotInitializedError, match=r'^worksheet is not initialized$'):
            getattr(driver, operation)(*args)
    finally:
        book.close()


def test_column_formats_are_saved_without_cells(tmp_path: Path) -> None:
    """Формат колонки сохраняется и на листе без записанных ячеек."""
    driver = XlsxWriterAdapter()
    driver.init_workbook(str(tmp_path), _FILE_NAME)
    driver.add_sheet('Пустой')
    driver.set_column_format({1: '@', 3: '#,##0.00'})
    driver.save()
    book = openpyxl.load_workbook(tmp_path / _FILE_NAME)
    try:
        sheet = book['Пустой']
        assert list(sheet.values) == []
        assert {column: dim.number_format for column, dim in sheet.column_dimensions.items()} == {
            'A': '@',
            'C': '#,##0.00',
        }
    finally:
        book.close()


@pytest.mark.parametrize('cell_value, width', _SHORT_VALUES)
def test_short_values_set_column_width(tmp_path: Path, cell_value: str | int | None, width: int) -> None:
    """Первая короткая или пустая ячейка тоже задаёт ширину колонки."""
    driver = XlsxWriterAdapter()
    driver.init_workbook(str(tmp_path), _FILE_NAME)
    driver.add_sheet('Коротко')
    driver.write(0, 0, cell_value)
    driver.save()
    book = openpyxl.load_workbook(tmp_path / _FILE_NAME)
    try:
        assert book['Коротко'].column_dimensions['A'].width == width
    finally:
        book.close()
