"""tests for make_parse_config factory"""

from unittest.mock import MagicMock

from parsers.base_parser.base_parser_config import (
    ParseParamsSupplier,
    ParserParams,
    make_parse_config,
)
from parsers.data_provider import MarkupRulesProviderFromUserConfig
from parsers.row_item.row_item import RowItem

_FOLDER_NAME = "acme_folder"
_SUPPLIER_NAME = "Acme Name"


def _parser_params() -> ParserParams:
    return ParserParams(
        supplier=ParseParamsSupplier(folder_name=_FOLDER_NAME, name=_SUPPLIER_NAME, code="99"),
        start_row=1,
        sheet_info="",
        columns={},
        stop_words=[],
        file_templates=[],
        sheet_indexes=[],
        row_item_adaptor=RowItem,
    )


def test_make_parse_config_keeps_parser_params() -> None:
    parser_params = _parser_params()
    assert make_parse_config(parser_params).parse_config.parser_params is parser_params


def test_markup_provider_uses_folder_name() -> None:
    provider = make_parse_config(_parser_params()).parse_config.markup_rules_provider
    assert isinstance(provider, MarkupRulesProviderFromUserConfig)
    assert provider.supplier_name == _FOLDER_NAME
    assert provider.supplier_name != _SUPPLIER_NAME


def test_make_parse_config_overrides_one_provider() -> None:
    stub = MagicMock()
    parse_config = make_parse_config(_parser_params(), black_list_provider=stub).parse_config
    assert parse_config.black_list_provider is stub
    assert isinstance(parse_config.markup_rules_provider, MarkupRulesProviderFromUserConfig)
