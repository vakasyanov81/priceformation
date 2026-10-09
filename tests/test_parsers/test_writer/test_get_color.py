"""tests for XlsWriter row color lookup."""

from typing import Any, ClassVar

import pytest

from parsers.writer.templates.iwrite_template import IWriteTemplate, WriteColors, WriteColumns
from parsers.writer.templates.tmpl.for_inner import ForInner
from parsers.writer.xls_writer import XlsWriter
from tests.fakes.fake_driver import FakeXlwtDriver

from .fixtures import ColorsWithoutMapTemplate, FixtureTemplate, write_data

_MIM_COLOR = '#f7d5d2'
_POSHK_COLOR = '#d9e2f3'
_COLOR_COLUMN = 0


class _EmptyColorColumnTemplate(IWriteTemplate):
    """by_column задан пустой строкой — окраска не применяется."""

    __COLUMNS__: ClassVar[WriteColumns] = FixtureTemplate.__COLUMNS__
    __COLOR__: ClassVar[WriteColors] = {
        'by_column': '',
        'with_map': {'x': '#ffffff'},
        'set_to_column_index': 0,
    }


def _make_writer(template: type[IWriteTemplate]) -> XlsWriter:
    return XlsWriter(FakeXlwtDriver(), write_data, template=template, result_folder='.')


@pytest.mark.parametrize(
    ('product', 'expected'),
    [
        ({'supplier_name': 'Мим'}, (_MIM_COLOR, _COLOR_COLUMN)),
        ({'supplier_name': 'Пошк'}, (_POSHK_COLOR, _COLOR_COLUMN)),
        ({'supplier_name': 'Unknown'}, (None, _COLOR_COLUMN)),
        ({'supplier_name': ''}, (None, None)),
        ({}, (None, None)),
    ],
)
def test_get_color_from_inner_map(
    product: dict[str, Any],
    expected: tuple[str | None, int | None],
) -> None:
    writer = _make_writer(ForInner)
    assert writer._get_color(product) == expected


def test_get_color_from_inner_write_data() -> None:
    writer = _make_writer(ForInner)
    assert writer._get_color(write_data[0]) == (_MIM_COLOR, _COLOR_COLUMN)


def test_get_color_without_template_colors() -> None:
    writer = _make_writer(FixtureTemplate)
    assert writer._get_color(write_data[0]) == (None, None)


def test_get_color_without_value_map() -> None:
    writer = _make_writer(ColorsWithoutMapTemplate)
    assert writer._get_color({'supplier_name': 'Мим'}) == (None, None)


def test_get_color_empty_column_name_is_no_color() -> None:
    """Пустое имя колонки цвета отключает окраску даже при ключе '' в строке."""
    writer = _make_writer(_EmptyColorColumnTemplate)
    assert writer._get_color({'': 'x'}) == (None, None)
