"""Finder and aliases are built once per parser/config, not per row."""

from typing import Any
from unittest.mock import MagicMock

from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.base_parser_config import (
    BasePriceParseConfigurationParams,
    ParseConfiguration,
    ParseParamsSupplier,
    ParserParams,
)
from parsers.base_parser.manufacturer_finder import ManufacturerFinder
from parsers.row_item.row_item import RowItem

_AEOLUS_ALIASES = {"Aeolus": ("Аеолус",)}


def _parser_params() -> ParserParams:
    return ParserParams(
        supplier=ParseParamsSupplier(folder_name="x", name="x", code="x"),
        start_row=1,
        sheet_info="",
        columns={},
        stop_words=[],
        file_templates=[],
        sheet_indexes=[0],
        row_item_adaptor=RowItem,
    )


def _configuration(aliases: dict[str, Any] | None = None) -> tuple[ParseConfiguration, MagicMock]:
    stub = MagicMock()
    stub.get_black_list_data.return_value = []
    stub.get_stop_words_data.return_value = []
    aliases_provider = MagicMock()
    if aliases is None:
        aliases_provider.get_aliases.return_value = _AEOLUS_ALIASES
    else:
        aliases_provider.get_aliases.return_value = aliases
    config = ParseConfiguration(
        BasePriceParseConfigurationParams(
            markup_rules_provider=stub,
            black_list_provider=stub,
            stop_words_provider=stub,
            vendor_list=stub,
            manufacturer_aliases=aliases_provider,
            parser_params=_parser_params(),
        )
    )
    return config, aliases_provider


def test_manufacturer_aliases_reads_provider_once() -> None:
    config, provider = _configuration()
    first = config.manufacturer_aliases()
    second = config.manufacturer_aliases()
    assert first is second
    assert first == _AEOLUS_ALIASES
    provider.get_aliases.assert_called_once()


def test_parser_reuses_manufacturer_finder() -> None:
    parser = BaseParser(parse_config=_configuration()[0])
    assert parser.manufacturer_finder() is parser.manufacturer_finder()


def test_set_parse_config_drops_cached_finder() -> None:
    parser = BaseParser(parse_config=_configuration()[0])
    first = parser.manufacturer_finder()
    parser.set_parse_config(_configuration({"Bridgestone": ("Бриджстоун",)})[0])
    second = parser.manufacturer_finder()
    assert first is not second


def test_prepare_builds_finder_once(monkeypatch: Any) -> None:
    created: list[int] = []
    original_init = ManufacturerFinder.__init__

    def counting_init(self: ManufacturerFinder, aliases: dict[str, Any] | None = None) -> None:
        created.append(1)
        original_init(self, aliases)

    monkeypatch.setattr(ManufacturerFinder, "__init__", counting_init)
    parser = BaseParser(parse_config=_configuration()[0])
    parser.prepare(
        [
            RowItem({"title": "Aeolus winter"}),
            RowItem({"title": "Aeolus summer"}),
        ]
    )
    assert created == [1]
