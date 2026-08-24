"""Contract tests for markup JSON key ``percent``."""

import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from parsers.base_parser.base_parser_config import (
    BasePriceParseConfigurationParams,
    ParseConfiguration,
    ParseParamsSupplier,
    ParserParams,
)
from parsers.data_provider.markup_rules import MarkUpParams, markup_params_from_rule
from parsers.row_item.row_item import RowItem

_MIM_FIRST = 0.2
_POSHK_FIRST = 0.7
_ZAPASKA_FIRST = 0.22
_PARSE_CONFIG_EXAMPLE = Path(__file__).resolve().parents[2] / "parse_config_example"


def _configuration_from_example(config_name: str) -> ParseConfiguration:
    markup_data = json.loads((_PARSE_CONFIG_EXAMPLE / config_name).read_text(encoding="utf-8"))
    markup_provider = MagicMock()
    markup_provider.get_markup_data.return_value = markup_data
    stub = MagicMock()
    parse_config = BasePriceParseConfigurationParams(
        markup_rules_provider=markup_provider,
        black_list_provider=stub,
        stop_words_provider=stub,
        vendor_list=stub,
        manufacturer_aliases=stub,
        parser_params=ParserParams(
            supplier=ParseParamsSupplier(folder_name="x", name="x", code="x"),
            start_row=0,
            sheet_info="",
            columns={},
            stop_words=[],
            file_templates=[],
            sheet_indexes=[0],
            row_item_adaptor=RowItem,
        ),
    )
    return ParseConfiguration(parse_config)


@pytest.mark.parametrize(
    ("config_name", "expected_first"),
    [
        ("mim_markup_rules.json", _MIM_FIRST),
        ("four_tochki_markup_rules.json", _MIM_FIRST),
        ("poshk_markup_rules.json", _POSHK_FIRST),
        ("zapaska_markup_rules.json", _ZAPASKA_FIRST),
    ],
)
def test_example_percent_key_loads(config_name: Any, expected_first: Any) -> None:
    markup_map = _configuration_from_example(config_name).get_price_markup_map()
    assert markup_map
    assert markup_map[0].percent_markup == pytest.approx(expected_first)


_RULE_MIN = 0
_RULE_MAX = 100
_RULE_PERCENT = 0.2
_BOTH_KEYS_PREFERRED = 0.1


def test_percent_keys_yield_same_params() -> None:
    from_percent = markup_params_from_rule(
        {"min": _RULE_MIN, "max": _RULE_MAX, "percent": _RULE_PERCENT},
    )
    from_alias = markup_params_from_rule(
        {"min": _RULE_MIN, "max": _RULE_MAX, "percent_markup": _RULE_PERCENT},
    )
    expected = MarkUpParams(min=_RULE_MIN, max=_RULE_MAX, percent_markup=_RULE_PERCENT)
    assert from_percent == from_alias == expected


def test_both_keys_prefer_percent_markup() -> None:
    markup = markup_params_from_rule(
        {
            "min": _RULE_MIN,
            "max": _RULE_MAX,
            "percent": _RULE_PERCENT,
            "percent_markup": _BOTH_KEYS_PREFERRED,
        },
    )
    assert markup.percent_markup == pytest.approx(_BOTH_KEYS_PREFERRED)
