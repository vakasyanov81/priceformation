"""План сохраняет границы групп и готовится целиком до записи."""

from dataclasses import replace
from unittest.mock import Mock

import pytest

from domain.exceptions import ConfigValidationError
from domain.product_group_result import TireAndDiskResult
from domain.product_groups import ProductGroup
from domain.row_item.row_item import RowItem
from parsers.common_price.tire_output import TireOutputSource
from parsers.data_provider.doubles_settings import DoublesSettings
from parsers.writer.output_plan import prepare_output_plan
from parsers.writer.templates.group_output import GroupOutput, OutputMode, TemplateOutput

TIRES = ProductGroup.TIRE_AND_DISK
BATTERIES = ProductGroup.BATTERIES


def _group() -> GroupOutput:
    columns = [{'Название': {'field': 'title'}}]
    return GroupOutput(TIRES, 'Шины', columns, {}, {}, file_name='tires_{now}.xlsx')


def test_empty_package_keeps_sheet_and_date() -> None:
    output = TemplateOutput('example', OutputMode.SEPARATE_FILES, (_group(),))
    books = prepare_output_plan([output], {TIRES: TireOutputSource(TireAndDiskResult())}, current_date='2026-11-12')
    assert books[0].file_name == 'tires_2026-11-12.xlsx'
    assert books[0].template_id == 'example'
    assert books[0].sheets[0].rows == ()
    sheet = books[0].sheets[0]
    assert sheet.settings.sheet_name == 'Шины'
    output.groups[0].columns.clear()
    assert sheet.settings.columns == [{'Название': {'field': 'title'}}]
    assert prepare_output_plan([], {}) == ()
    sources = {TIRES: TireOutputSource(TireAndDiskResult())}
    empty_output = TemplateOutput('empty', OutputMode.SEPARATE_FILES, (_group(),))
    assert prepare_output_plan([empty_output], sources, selected=set()) == ()


@pytest.mark.parametrize('mode, expected_count', [(OutputMode.SEPARATE_FILES, 2), (OutputMode.WORKBOOK_SHEETS, 1)])
def test_group_sources_have_independent_settings(mode: OutputMode, expected_count: int) -> None:
    tires = _group()
    columns = [{'Имя': {'field': 'label'}}]
    other = GroupOutput(BATTERIES, 'Другая модель', columns, {}, {}, file_name='other.xlsx')
    file_name = None
    if mode == OutputMode.WORKBOOK_SHEETS:
        tires = replace(tires, file_name=None)
        other = replace(other, file_name=None)
        file_name = 'all.xlsx'
    output = TemplateOutput('example', mode, (tires, other), file_name)
    other_source = Mock(fields=frozenset(('label',)))
    other_source.prepare.return_value = ({'label': 'Другая модель'},)
    source = TireOutputSource(TireAndDiskResult((RowItem({'title': 'Шина'}),)))
    books = prepare_output_plan([output], {TIRES: source, BATTERIES: other_source})
    sheets = [sheet for book in books for sheet in book.sheets]
    assert len(books) == expected_count
    assert sheets[0].rows[0]['title'] == 'Шина'
    assert sheets[1].rows == ({'label': 'Другая модель'},)
    assert sheets[1].settings.columns == other.columns
    other_source.prepare.assert_called_once_with('example', other)


def test_all_templates_validated_before_preparing_positions() -> None:
    source = Mock(fields=frozenset(('title',)))
    output = TemplateOutput('example', OutputMode.SEPARATE_FILES, (_group(),))
    collision = replace(output, template_id='collision')
    with pytest.raises(ConfigValidationError, match='путь'):
        prepare_output_plan([output, collision], {TIRES: source})
    source.prepare.assert_not_called()


def test_tire_filters_use_merged_values_before_serialization() -> None:
    rows = tuple(
        RowItem({'code': 'one', 'supplier_name': 'vendor', 'warehouse_group': 'group', 'rest_count': 1})
        for _index in range(2)
    )
    source = TireOutputSource(TireAndDiskResult(rows))
    settings = replace(_group(), merge_warehouses=True, filters={'rest_count': [1]})
    prepared = source.prepare('example', settings)
    assert len(prepared) == 1
    assert prepared[0]['rest_count'] == 2
    assert [row.stock.rest_count for row in rows] == [1, 1]
    exclude_merged = replace(settings, filters={'rest_count': [2]})
    assert source.prepare('example', exclude_merged) == ()


def test_tire_duplicates_respect_template_choice() -> None:
    fields = {'is_double': True, 'group_by_params': 0}
    rows = tuple(RowItem(fields) for _index in range(2))
    source = TireOutputSource(TireAndDiskResult(rows), DoublesSettings(('example',)))
    assert len(source.prepare('example', _group())) == 1
    assert len(source.prepare('other', _group())) == 2
    with pytest.raises(ValueError, match='другой группы'):
        source.prepare('example', replace(_group(), id=BATTERIES))
