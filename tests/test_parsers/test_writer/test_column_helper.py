"""tests for write-column helper."""

from parsers.row_item.row_item import RowItem
from parsers.writer.templates.column_helper import ColumnHelper
from parsers.writer.templates.tmpl.for_inner import ForInner

_STYLE_WIDTH = 256 * 15


def test_column_helper_reads_inner_type_column() -> None:
    helper = ColumnHelper(ForInner.__COLUMNS__[0])
    assert helper.name == "Тип товара"
    assert helper.field == RowItem.type_production.name
    assert helper.style == {"width": 256 * 10}
    assert helper.style_width == 256 * 10
    assert not helper.skip
    assert helper.format is None
    assert helper.def_value is None


def test_column_helper_reads_optional_keys() -> None:
    helper = ColumnHelper(
        {
            "Цена": {
                "style": {"width": _STYLE_WIDTH},
                "field": RowItem.price_opt.name,
                "format": "@",
                "skip": True,
                "default_value": "0",
            }
        }
    )
    assert helper.name == "Цена"
    assert helper.field == RowItem.price_opt.name
    assert helper.style_width == _STYLE_WIDTH
    assert helper.format == "@"
    assert helper.skip
    assert helper.def_value == "0"


def test_column_helper_defaults_when_keys_missing() -> None:
    helper = ColumnHelper({"Номенклатура": {"field": RowItem.title.name}})
    assert helper.name == "Номенклатура"
    assert helper.field == RowItem.title.name
    assert helper.style == {}
    assert helper.style_width is None
    assert not helper.skip
    assert helper.format is None
    assert helper.def_value is None


def test_inner_columns_format_is_one_based() -> None:
    assert ForInner().get_columns_format() == {6: "@", 8: "@"}
