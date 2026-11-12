"""Ошибки входных маршрутов и выходных шаблонов на реальном XLSX."""

from dataclasses import replace
from pathlib import Path
from unittest.mock import Mock

import pytest

from domain.exceptions import ConfigValidationError
from integration_tests.group_xlsx_examples import DATE, group_writer, output_sources, output_template
from integration_tests.product_group_examples import supplier_price
from parsers.base_parser.file_reader import FileReader
from parsers.base_parser.price_files import PriceFiles
from parsers.base_parser.routing import VendorRouting
from parsers.base_parser.routing_rows import RowRoutingError
from parsers.base_parser.section_params import parser_params_from_section
from parsers.vendor_config.models import VendorConfig
from parsers.writer.templates.group_output import OutputMode, TemplateOutput

_TITLE = 'title'
_ID = 'id'
_START_ROW = 'start_row'


@pytest.fixture(params=list(OutputMode))
def output_mode(request: pytest.FixtureRequest) -> OutputMode:
    return OutputMode(request.param)


def _invalid_template(mode: OutputMode, problem: str) -> TemplateOutput:
    output = output_template(mode)
    other = output.groups[1]
    first = output.groups[0]
    changes = {
        'columns': replace(other, columns=[{'Чужое поле': {'field': _TITLE}}]),
        'filters': replace(other, filters={_TITLE: []}),
        'formatting': replace(other, formatting={'by_column': _TITLE}),
        'sheet_name': replace(other, sheet_name='a/b'),
        'collision': replace(other, file_name=first.file_name, sheet_name=first.sheet_name.upper()),
    }
    return replace(output, groups=(output.groups[0], changes[problem]))


@pytest.mark.parametrize('problem', ['columns', 'filters', 'formatting', 'sheet_name', 'collision'])
def test_template_error_preserves_files(tmp_path: Path, output_mode: OutputMode, problem: str) -> None:
    """Ошибка второй группы не портит существующую первую книгу и не пишет новых."""
    sources = output_sources(tmp_path / 'input.xlsx')
    folder = tmp_path / 'result'
    folder.mkdir()
    existing_name = f'all_{DATE}.xlsx' if output_mode is OutputMode.WORKBOOK_SHEETS else f'tires_{DATE}.xlsx'
    existing = folder / existing_name
    existing.write_bytes(b'existing workbook')
    with pytest.raises(ConfigValidationError, match='integration'):
        group_writer(folder).write([_invalid_template(output_mode, problem)], sources, current_date=DATE)
    assert existing.read_bytes() == b'existing workbook'
    assert list(folder.iterdir()) == [existing]


def _route_config(problem: str) -> VendorConfig:
    sections: list[dict[str, object]] = [{_ID: 'tires'}, {_ID: 'other'}]
    if problem != 'missing':
        sections[0]['row_selector'] = {'column': '0', 'values': ['same']}
        source_column = '1' if problem == 'dynamic' else '0'
        sections[1]['row_selector'] = {'column': source_column, 'values': ['same']}
    if problem == _START_ROW:
        sections[1][_START_ROW] = 3
    return VendorConfig.from_dict(
        {
            'code': 'demo',
            'name': 'Поставщик',
            'defaults': {_START_ROW: 2, 'file_templates': ['*.xlsx']},
            'product_groups': [
                {_ID: 'tire_and_disk', 'columns': {'0': _TITLE}, 'sections': [sections[0]]},
                {_ID: 'batteries', 'sections': [sections[1]]},
            ],
        },
        'demo',
        'demo.json',
    )


@pytest.mark.parametrize(
    'problem, exception, message',
    [
        ('missing', ConfigValidationError, 'row_selector'),
        ('overlap', ConfigValidationError, 'пересекаются'),
        (_START_ROW, ConfigValidationError, _START_ROW),
        ('dynamic', RowRoutingError, 'строка 3'),
    ],
)
def test_ambiguous_input_precedes_models(
    tmp_path: Path, problem: str, exception: type[Exception], message: str
) -> None:
    """Физический лист проверяется по всем группам до создания первой позиции."""
    supplier_price(tmp_path / 'input.xlsx')
    config = _route_config(problem)
    files = PriceFiles(
        parser_params_from_section(config.sections[0], config.folder),
        FileReader(price_source=Mock()),
        VendorRouting(config),
    )
    files.files = [str(tmp_path / 'input.xlsx')]
    files.resolve()
    create_position = Mock()
    with pytest.raises(exception, match=message):
        files.read_positions(files.files, create_position)
    create_position.assert_not_called()
