"""Markup cache lives on the ParseConfiguration instance, not the class."""

from typing import Any
from unittest.mock import MagicMock

import pytest

from parsers.base_parser.base_parser_config import (
    BasePriceParseConfigurationParams,
    ParseConfiguration,
    ParseParamsSupplier,
    ParserParams,
)
from parsers.row_item.row_item import RowItem

_PERCENT_LOW = 0.1
_PERCENT_HIGH = 0.9


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


def _markup_data(percent: float) -> dict[str, Any]:
    return {"markup_rules": {"shelf": {"min": 0, "max": 1, "percent": percent}}}


def _configuration(markup_data: dict[str, Any]) -> tuple[ParseConfiguration, MagicMock]:
    provider = MagicMock()
    provider.get_markup_data.return_value = markup_data
    stub = MagicMock()
    config = ParseConfiguration(
        BasePriceParseConfigurationParams(
            markup_rules_provider=provider,
            black_list_provider=stub,
            stop_words_provider=stub,
            vendor_list=stub,
            manufacturer_aliases=stub,
            parser_params=_parser_params(),
        )
    )
    return config, provider


def test_two_configs_keep_own_markup() -> None:
    low = _configuration(_markup_data(_PERCENT_LOW))[0]
    high = _configuration(_markup_data(_PERCENT_HIGH))[0]

    assert low.get_price_markup_map()[0].percent_markup == pytest.approx(_PERCENT_LOW)
    assert high.get_price_markup_map()[0].percent_markup == pytest.approx(_PERCENT_HIGH)


def test_markup_provider_called_once() -> None:
    config, provider = _configuration(_markup_data(_PERCENT_LOW))
    config.get_price_markup_map()
    config.get_price_markup_map()
    assert provider.get_markup_data.call_count == 1


def test_empty_price_markup_map_is_cached() -> None:
    config, provider = _configuration({"markup_rules": {}})
    first = config.get_price_markup_map()
    second = config.get_price_markup_map()
    assert first == ()
    assert second is first
    assert provider.get_markup_data.call_count == 1
