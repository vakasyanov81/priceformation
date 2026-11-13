"""Ошибки шаблона выявляются до создания результата."""

from dataclasses import replace
from typing import TypedDict, Unpack

import pytest

from domain.exceptions import ConfigValidationError
from domain.product_groups import ProductGroup
from parsers.writer.output_names import output_file_name, validate_sheet_name
from parsers.writer.output_validation import validate_outputs
from parsers.writer.templates.all_templates import all_writer_templates
from parsers.writer.templates.group_output import (
    GroupOutput,
    OutputMode,
    TemplateOutput,
    WriteColors,
    WriteColumns,
    WriteExclude,
)
from parsers.writer.templates.tmpl.for_doubles import ForDoubles
from parsers.writer.templates.tmpl.for_full import ForFull

TIRES = ProductGroup.TIRE_AND_DISK
BATTERIES = ProductGroup.BATTERIES
SCHEMAS = {TIRES: frozenset(('title',)), BATTERIES: frozenset(('label',))}


class GroupChanges(TypedDict, total=False):
    """Типизированные переопределения проверяемого описания."""

    columns: WriteColumns
    filters: WriteExclude
    formatting: WriteColors
    sheet_name: str
    file_name: str | None


def _group(group: ProductGroup = TIRES, **changes: Unpack[GroupChanges]) -> GroupOutput:
    columns = [{'Название': {'field': 'title'}}]
    base = GroupOutput(group, 'price', columns, {}, {}, file_name='price_{now}.xlsx')
    return replace(base, **changes)


def _output(*groups: GroupOutput) -> TemplateOutput:
    return TemplateOutput('example', OutputMode.SEPARATE_FILES, groups or (_group(),))


def test_current_templates_pass_preflight() -> None:
    """Действующие файлы не конфликтуют и используют поля шинной схемы."""
    templates = [*all_writer_templates(), ForFull, ForDoubles]
    validate_outputs([template().output_spec() for template in templates], {TIRES})


@pytest.mark.parametrize(
    'name',
    (
        '',
        ' ',
        'a' * 32,
        'History',
        'hIsToRy',
        "'price",
        "price'",
        'a/b',
        'a\\b',
        'a:b',
        'a?b',
        'a*b',
        '[a]',
        'a\nb',
    ),
)
def test_invalid_sheet_name(name: str) -> None:
    with pytest.raises(ConfigValidationError, match='sheet_name'):
        validate_sheet_name(name, 'example')


def test_sheet_name_allows_excel_maximum_length() -> None:
    validate_sheet_name('a' * 31, 'example')


@pytest.mark.parametrize(
    'pattern',
    [
        '../x.xlsx',
        '/x.xlsx',
        'a\\b.xlsx',
        'CON.xlsx',
        'lpt1.xlsx',
        'price.xls',
        'a.xlsx ',
        'a?.xlsx',
        'a\nb.xlsx',
        '{other}.xlsx',
        '{now!r}.xlsx',
        '{now:10}.xlsx',
        '{.xlsx',
    ],
)
def test_invalid_file_name(pattern: str) -> None:
    with pytest.raises(ConfigValidationError, match='file_name'):
        output_file_name(pattern, '2026-11-12', 'example')


def test_file_date_substitution() -> None:
    assert output_file_name('price_{now}.xlsx', '2026-11-12', 'example') == 'price_2026-11-12.xlsx'


@pytest.mark.parametrize(
    'changes, path',
    [
        ({'columns': [{'A': {'field': 'label'}}]}, 'columns'),
        ({'columns': [{'A': {'suffix_when': 'label'}}]}, 'suffix_when'),
        ({'columns': [{}]}, 'columns'),
        ({'filters': {'label': []}}, 'filters'),
        ({'formatting': {'by_column': 'label'}}, 'formatting'),
        ({'formatting': {'rules': [{'by_column': 'label'}]}}, 'formatting'),
    ],
)
def test_foreign_fields_rejected(changes: GroupChanges, path: str) -> None:
    with pytest.raises(ConfigValidationError, match=f'example.*tire_and_disk.*{path}'):
        validate_outputs([_output(_group(**changes))], {TIRES}, schemas=SCHEMAS)


def test_unavailable_converter_rejected() -> None:
    with pytest.raises(ConfigValidationError, match=r'batteries.*преобразователя'):
        validate_outputs([_output(_group(BATTERIES))], {BATTERIES})


def test_supported_subset_must_be_explicit() -> None:
    with pytest.raises(ConfigValidationError, match=r'example.*batteries'):
        validate_outputs([_output()], {TIRES, BATTERIES}, schemas=SCHEMAS)
    validate_outputs([_output()], {TIRES}, schemas=SCHEMAS)


def test_collision_after_date_substitution() -> None:
    first = _output()
    second = replace(_output(_group(file_name='PRICE_2026-11-12.xlsx')), template_id='second')
    with pytest.raises(ConfigValidationError, match=r'second.*example'):
        validate_outputs([first, second], {TIRES}, current_date='2026-11-12')


def test_group_files_cannot_share_path() -> None:
    batteries = _group(BATTERIES, columns=[{'Имя': {'field': 'label'}}])
    with pytest.raises(ConfigValidationError, match='путь'):
        validate_outputs([_output(_group(), batteries)], {TIRES, BATTERIES}, schemas=SCHEMAS)


def test_workbook_sheets_and_jsonl_paths_are_independent() -> None:
    groups = (
        _group(file_name=None),
        _group(BATTERIES, columns=[{'Имя': {'field': 'label'}}], file_name=None, sheet_name='АКБ'),
    )
    workbook = TemplateOutput('example', OutputMode.WORKBOOK_SHEETS, groups, 'price.xlsx')
    validate_outputs([workbook], {TIRES, BATTERIES}, schemas=SCHEMAS)
    other = replace(_output(_group(file_name='price_tire_and_disk.xlsx')), template_id='other')
    with pytest.raises(ConfigValidationError, match='jsonl'):
        validate_outputs([workbook, other], {TIRES}, schemas=SCHEMAS)
    duplicate_sheet = replace(groups[1], sheet_name='PRICE')
    with pytest.raises(ConfigValidationError, match='sheet_name'):
        invalid = replace(workbook, groups=(groups[0], duplicate_sheet))
        validate_outputs([invalid], {TIRES}, schemas=SCHEMAS)


@pytest.mark.parametrize(
    'output',
    [
        TemplateOutput('example', OutputMode.SEPARATE_FILES, ()),
        _output(_group(), _group()),
        replace(_output(), file_name='price.xlsx'),
        _output(_group(file_name=None)),
        TemplateOutput('example', OutputMode.WORKBOOK_SHEETS, (_group(),), 'price.xlsx'),
    ],
)
def test_invalid_structure(output: TemplateOutput) -> None:
    with pytest.raises(ConfigValidationError, match='example'):
        validate_outputs([output], {TIRES})


def test_repeated_template_identifier_rejected() -> None:
    with pytest.raises(ConfigValidationError, match='template_id'):
        validate_outputs([_output(), _output()], {TIRES})


def test_no_selection_has_no_path_collisions() -> None:
    batteries = _group(BATTERIES, columns=[{'Имя': {'field': 'label'}}])
    groups = (_group(), batteries)
    validate_outputs([_output(*groups)], set(), schemas=SCHEMAS)


def test_unselected_group_filename_is_still_validated() -> None:
    with pytest.raises(ConfigValidationError, match='file_name'):
        validate_outputs([_output(_group(file_name='../price.xlsx'))], set())


def test_control_character_outside_ascii_is_rejected() -> None:
    with pytest.raises(ConfigValidationError, match='sheet_name'):
        validate_sheet_name('price\x85', 'example')
