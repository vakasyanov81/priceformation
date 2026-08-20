"""tests for BaseParser.get_xls_reader arguments."""

from unittest.mock import MagicMock

from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.base_parser_config import (
    BasePriceParseConfigurationParams,
    ParseConfiguration,
    ParseParamsSupplier,
    ParserParams,
)
from parsers.row_item.row_item import RowItem

_START_ROW = 3
_COLUMNS = {0: "title", 5: "price"}
_XLS_PATH = "prices/vendor.xls"


def _parse_config() -> ParseConfiguration:
    stub = MagicMock()
    return ParseConfiguration(
        BasePriceParseConfigurationParams(
            markup_rules_provider=stub,
            black_list_provider=stub,
            stop_words_provider=stub,
            vendor_list=stub,
            manufacturer_aliases=stub,
            parser_params=ParserParams(
                supplier=ParseParamsSupplier(folder_name="x", name="x", code="x"),
                start_row=_START_ROW,
                sheet_info="",
                columns=_COLUMNS,
                stop_words=[],
                file_templates=[],
                sheet_indexes=[0],
                row_item_adaptor=RowItem,
            ),
        )
    )


def test_get_xls_reader_passes_path_and_params() -> None:
    xls_reader = MagicMock()
    instance = MagicMock()
    xls_reader.get_instance.return_value = instance
    parser = BaseParser(parse_config=_parse_config(), xls_reader=xls_reader)

    assert parser.get_xls_reader(_XLS_PATH) is instance
    xls_reader.get_instance.assert_called_once_with(
        _XLS_PATH,
        {
            "start_row": _START_ROW - 1,
            "columns": _COLUMNS,
        },
    )
