"""Реальные книги разных моделей остаются независимыми."""

from dataclasses import replace
from pathlib import Path
from unittest.mock import Mock

import openpyxl
import pytest

from domain.exceptions import ConfigValidationError
from domain.product_group_result import TireAndDiskResult
from domain.product_groups import ProductGroup
from domain.row_item.row_item import RowItem
from parsers.common_price.tire_output import TireOutputSource
from parsers.writer.group_files import GroupFileWriter
from parsers.writer.output_plan import GroupOutputSource
from parsers.writer.templates.group_output import GroupOutput, OutputMode, TemplateOutput
from parsers.writer.xls_writer import XlsWriter
from parsers.writer.xlsxwriter_adapter import XlsxWriterAdapter
from tests.group_output_examples import OtherOutputSource
from tests.test_domain.group_handler_examples import TestGroupResult, TestPosition

TIRES = ProductGroup.TIRE_AND_DISK
OTHER = ProductGroup.BATTERIES
DATE = '2026-11-12'


def _output() -> TemplateOutput:
    tires = GroupOutput(
        TIRES,
        'Шины',
        [{'Шинное название': {'field': 'title', 'format': '@'}}],
        {},
        {'by_column': 'title', 'with_map': {'Шина': '00FF00'}},
        file_name='tires_{now}.xlsx',
    )
    other = GroupOutput(
        OTHER,
        'Тестовая модель',
        [{'Метка': {'field': 'label'}}],
        {'label': ['пропустить']},
        {},
        file_name='other_{now}.xlsx',
    )
    return TemplateOutput('example', OutputMode.SEPARATE_FILES, (tires, other))


def _sources() -> dict[ProductGroup, GroupOutputSource]:
    package = TestGroupResult((TestPosition('Шина'), TestPosition('пропустить')))
    return {
        TIRES: TireOutputSource(TireAndDiskResult((RowItem({'title': 'Шина'}),))),
        OTHER: OtherOutputSource(package),
    }


def _writer(folder: Path) -> GroupFileWriter:
    return GroupFileWriter(xls_writer=XlsWriter, write_driver=XlsxWriterAdapter, result_folder=str(folder))


def test_two_models_write_two_independent_books(tmp_path: Path) -> None:
    folder = tmp_path / 'result'
    paths = _writer(folder).write([_output()], _sources(), current_date=DATE)
    expected = [folder / f'tires_{DATE}.xlsx', folder / f'other_{DATE}.xlsx']
    assert paths == [str(path) for path in expected]
    tires = openpyxl.load_workbook(paths[0])
    other = openpyxl.load_workbook(paths[1])
    try:
        assert tires.sheetnames == ['Шины']
        assert other.sheetnames == ['Тестовая модель']
        tire_sheet = tires['Шины']
        other_sheet = other['Тестовая модель']
        assert list(tire_sheet.values) == [('Шинное название',), ('Шина',)]
        assert list(other_sheet.values) == [('Метка',), ('Шина',)]
        assert tire_sheet['A2'].number_format == '@'
        assert tire_sheet['A2'].fill.fgColor.rgb == 'FF00FF00'
        assert other_sheet['A2'].number_format == 'General'
        assert other_sheet['A2'].fill.fill_type is None
    finally:
        tires.close()
        other.close()


def test_selected_empty_group_writes_headers_only(tmp_path: Path) -> None:
    sources = _sources()
    sources[OTHER] = OtherOutputSource(TestGroupResult(()))
    writer = _writer(tmp_path)
    paths = writer.write([_output()], sources, selected={OTHER}, current_date=DATE)
    assert len(paths) == 1
    assert Path(paths[0]).name == f'other_{DATE}.xlsx'
    book = openpyxl.load_workbook(paths[0])
    try:
        assert list(book['Тестовая модель'].values) == [('Метка',)]
    finally:
        book.close()


def test_no_selection_creates_no_folder(tmp_path: Path) -> None:
    folder = tmp_path / 'result'
    writer = _writer(folder)
    assert writer.write([_output()], _sources(), selected=set()) == []
    assert not folder.exists()


def test_conflicting_group_paths_preserve_existing_files(tmp_path: Path) -> None:
    output = _output()
    collision = replace(output.groups[1], file_name=f'TIRES_{DATE}.xlsx')
    output = replace(output, groups=(output.groups[0], collision))
    existing = tmp_path / f'tires_{DATE}.xlsx'
    existing.write_bytes(b'existing workbook')
    driver = Mock()
    writer = GroupFileWriter(xls_writer=XlsWriter, write_driver=driver, result_folder=str(tmp_path))
    with pytest.raises(ConfigValidationError, match='путь'):
        writer.write([output], _sources(), current_date=DATE)
    driver.assert_not_called()
    assert existing.read_bytes() == b'existing workbook'
    assert list(tmp_path.iterdir()) == [existing]


def test_unknown_field_of_second_model_fails_before_creating_folder(tmp_path: Path) -> None:
    output = _output()
    columns = [{'Чужое поле': {'field': 'title'}}]
    other = replace(output.groups[1], columns=columns)
    output = replace(output, groups=(output.groups[0], other))
    folder = tmp_path / 'result'
    with pytest.raises(ConfigValidationError, match=r'batteries.*columns'):
        _writer(folder).write([output], _sources())
    assert not folder.exists()


@pytest.mark.parametrize(
    'empty_other, expected',
    [(False, [('Метка',), ('Шина',)]), (True, [('Метка',)])],
)
def test_workbook_sheets_keep_models_and_styles_independent(
    tmp_path: Path, empty_other: bool, expected: list[tuple[str]]
) -> None:
    output = _output()
    groups = tuple(replace(group, file_name=None) for group in output.groups)
    output = replace(output, mode=OutputMode.WORKBOOK_SHEETS, groups=groups, file_name='all_{now}.xlsx')
    sources = _sources()
    if empty_other:
        sources[OTHER] = OtherOutputSource(TestGroupResult(()))
    folder = tmp_path / 'nested' / 'result'
    paths = _writer(folder).write([output], sources, current_date=DATE)
    assert paths == [str(folder / f'all_{DATE}.xlsx')]
    book = openpyxl.load_workbook(paths[0])
    try:
        assert book.sheetnames == ['Шины', 'Тестовая модель']
        tires = book['Шины']
        other = book['Тестовая модель']
        assert list(tires.values) == [('Шинное название',), ('Шина',)]
        assert list(other.values) == expected
        assert tires['A2'].number_format == '@'
        assert tires['A2'].fill.fgColor.rgb == 'FF00FF00'
        assert other['A2'].number_format == 'General'
        assert other['A2'].fill.fill_type is None
    finally:
        book.close()
