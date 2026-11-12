"""Контракт группового описания существующих шаблонов."""

import pytest

from domain.product_groups import ProductGroup
from parsers.writer.templates.all_templates import all_writer_templates, writer_template_name
from parsers.writer.templates.group_output import GroupOutput, OutputMode, TemplateOutput
from parsers.writer.templates.iwrite_template import IWriteTemplate
from parsers.writer.templates.tmpl.for_doubles import ForDoubles
from parsers.writer.templates.tmpl.for_full import ForFull


@pytest.mark.parametrize('template', [*all_writer_templates(), ForFull, ForDoubles])
def test_existing_template_describes_tire_and_disk(template: type[IWriteTemplate]) -> None:
    """Колонки и имена существующего вывода сохраняются в групповом контракте."""
    instance = template()
    output = instance.output_spec()
    assert output.template_id == writer_template_name(template)
    assert output.mode == OutputMode.SEPARATE_FILES
    assert output.file_name is None
    assert len(output.groups) == 1
    group = output.groups[0]
    assert group.id == ProductGroup.TIRE_AND_DISK
    assert group.sheet_name == 'price'
    assert group.file_name == instance.get_file_name()
    assert group.columns == instance.columns()
    assert group.filters == instance.exclude()
    assert group.formatting == instance.colors()
    assert group.merge_warehouses == instance.__MERGE_WAREHOUSES__
    group.columns[0].clear()
    group.filters['foreign'] = []
    group.formatting['foreign'] = []
    assert instance.output_spec().groups[0].columns == instance.columns()
    assert 'foreign' not in instance.exclude()
    assert 'foreign' not in instance.colors()


def test_workbook_description_keeps_group_settings_separate() -> None:
    """Описание допускает разные выходные схемы внутри общей книги."""
    columns = [{'Название': {'field': 'title'}}]
    tires = GroupOutput(ProductGroup.TIRE_AND_DISK, 'Шины', columns, {}, {})
    batteries = GroupOutput(ProductGroup.BATTERIES, 'Аккумуляторы', [], {}, {})
    output = TemplateOutput('example', OutputMode.WORKBOOK_SHEETS, (tires, batteries), 'price_{now}.xlsx')
    assert output.groups[0].columns != output.groups[1].columns
    assert all(group.file_name is None for group in output.groups)
    assert output.file_name == 'price_{now}.xlsx'
