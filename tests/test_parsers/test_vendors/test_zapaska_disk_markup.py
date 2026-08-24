"""tests for zapaska disk markup via MarkupPolicy + JSON."""

import json
from pathlib import Path

import pytest

from parsers.base_parser.base_parser_config import extract_markup_rules
from parsers.base_parser.markup_policy import MarkupPolicy
from parsers.data_provider.markup_rules import markup_params_from_rule

_OPT = 1000
_ENOUGH_RECOMMENDED = 2000
_EXACT_EIGHT_PERCENT = 1080
_ABOVE_EIGHT_PERCENT = 1081
_SMALL_MARGIN_PRICE = 1100
_LARGE_MARGIN_PRICE = 1300
_ABSOLUTE_FLOOR = 1150
_NO_RRC_OPT = 10000
_NO_RRC_PRICE = 11600
_RULES_PATH = Path(__file__).with_name("zapaska_markup_rules.json")


def _zapaska_policy() -> MarkupPolicy:
    markup_data = json.loads(_RULES_PATH.read_text(encoding="utf-8"))
    rules = extract_markup_rules(markup_data)
    price_map = tuple(markup_params_from_rule(rule) for rule in rules.markup_rules.values())
    return MarkupPolicy(rules, price_map)


@pytest.mark.parametrize(
    ("price_opt", "percent"),
    [
        (0, 0.12),
        (4999, 0.22),
        (5000, 0.20),
        (9999, 0.20),
        (10000, 0.16),
        (14999, 0.16),
        (15000, 0.14),
        (19999, 0.14),
        (20000, 0.12),
        (24999, 0.12),
        (25000, 0.12),
    ],
)
def test_price_percent_markup_by_range(price_opt: float, percent: float) -> None:
    assert _zapaska_policy().markup_percent_for_opt(price_opt) == pytest.approx(percent)


def test_absolute_markup_small_margin() -> None:
    assert _zapaska_policy().apply(_OPT, _SMALL_MARGIN_PRICE) == _ABSOLUTE_FLOOR


def test_absolute_markup_at_delta() -> None:
    assert _zapaska_policy().apply(_OPT, _ABSOLUTE_FLOOR) == _ABSOLUTE_FLOOR


def test_absolute_markup_keeps_price() -> None:
    assert _zapaska_policy().apply(_OPT, _LARGE_MARGIN_PRICE) == _LARGE_MARGIN_PRICE


def test_small_recommended_at_threshold() -> None:
    assert _zapaska_policy().apply(_OPT, _EXACT_EIGHT_PERCENT) == _ABSOLUTE_FLOOR


def test_small_recommended_above_limit() -> None:
    assert _zapaska_policy().apply(_OPT, _ABOVE_EIGHT_PERCENT) == _ABSOLUTE_FLOOR


def test_recommended_markup_keeps_price() -> None:
    assert _zapaska_policy().apply(_OPT, _ENOUGH_RECOMMENDED) == _ENOUGH_RECOMMENDED


def test_no_recommended_uses_map() -> None:
    assert _zapaska_policy().apply(_NO_RRC_OPT, None) == _NO_RRC_PRICE
