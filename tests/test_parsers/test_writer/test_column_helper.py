"""tests for write-column helper."""

import pytest

from parsers.row_item.row_item import RowItem
from parsers.writer.templates.column_helper import ColumnHelper
from parsers.writer.templates.iwrite_template import IWriteTemplate
from parsers.writer.templates.tmpl.for_doubles import ForDoubles
from parsers.writer.templates.tmpl.for_drom import ForDrom
from parsers.writer.templates.tmpl.for_full import ForFull
from parsers.writer.templates.tmpl.for_inner import ForInner

_STYLE_WIDTH = 256 * 15
_ALL_TEMPLATES = (ForInner, ForDrom, ForFull, ForDoubles)


def test_column_helper_reads_inner_type_column() -> None:
    helper = ColumnHelper(ForInner.__COLUMNS__[0])
    assert helper.name == 'Тип товара'
    assert helper.field == RowItem.type_production.name
    assert helper.style == {'width': 256 * 10}
    assert helper.style_width == 256 * 10
    assert not helper.skip
    assert helper.format is None
    assert helper.def_value is None


def test_column_helper_reads_optional_keys() -> None:
    helper = ColumnHelper(
        {
            'Цена': {
                'style': {'width': _STYLE_WIDTH},
                'field': RowItem.price_opt.name,
                'format': '@',
                'skip': True,
                'default_value': '0',
            }
        }
    )
    assert helper.name == 'Цена'
    assert helper.field == RowItem.price_opt.name
    assert helper.style_width == _STYLE_WIDTH
    assert helper.format == '@'
    assert helper.skip
    assert helper.def_value == '0'


def test_column_helper_defaults_when_keys_missing() -> None:
    helper = ColumnHelper({'Номенклатура': {'field': RowItem.title.name}})
    assert helper.name == 'Номенклатура'
    assert helper.field == RowItem.title.name
    assert helper.style == {}
    assert helper.style_width is None
    assert not helper.skip
    assert helper.format is None
    assert helper.def_value is None


@pytest.mark.parametrize('template', _ALL_TEMPLATES)
def test_template_column_has_single_key(template: type[IWriteTemplate]) -> None:
    """в описании колонки один ключ: 'format' и 'style' живут внутри значения, а не рядом с именем."""
    for column in template().columns():
        assert len(column) == 1


@pytest.mark.parametrize('template', _ALL_TEMPLATES)
def test_column_helper_reads_options_of_nested_column(template: type[IWriteTemplate]) -> None:
    """хелпер читает опции из значения колонки, а не из её соседей по словарю."""
    for column in template().columns():
        options = next(iter(column.values()))
        helper = ColumnHelper(column)
        assert helper.name == next(iter(column))
        assert helper.field == options.get('field')
        assert helper.format == options.get('format')
        assert helper.def_value == options.get('default_value')
        assert helper.style == (options.get('style') or {})
        assert helper.skip is bool(options.get('skip'))


@pytest.mark.parametrize(
    'template, expected',
    [
        (ForInner, {6: '@', 8: '@'}),
        (ForDrom, {6: '@'}),
        (ForFull, {}),
        (ForDoubles, {6: '@', 8: '@'}),
    ],
)
def test_template_price_columns_are_text(
    template: type[IWriteTemplate],
    expected: dict[int, str],
) -> None:
    """цены выводятся текстом: format '@' задан у колонок с ценой каждого шаблона."""
    assert template().get_columns_format() == expected


def test_drom_price_column_has_text_format() -> None:
    """у колонки «Цена» шаблона drom format лежит внутри значения, а не рядом с именем."""
    price = ForDrom().get_columns()['Цена']
    assert price.format == '@'
    assert price.field == RowItem.price_markup.name
