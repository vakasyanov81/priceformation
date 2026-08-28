"""tests for markup rules provider"""

from unittest.mock import patch

import pytest

from core.exceptions import CoreExceptionError
from core.parse_paths import ParsePaths
from parsers import data_provider
from parsers.base_parser.base_parser_config import extract_markup_rules
from parsers.data_provider.markup_rules import (
    MarkupRulesProviderBase,
    MarkupRulesProviderFromUserConfig,
    PriceRulesConfigFileError,
    markup_params_from_rule,
)

_TO_LOG = "to_log"
_PERCENT = 0.2
_PERCENT_ALT = 0.15
_PREFERRED = 0.1
_RULE_MAX = 50
_MISSING_FILE = "/no"
_STK_RULES_PATH = "/cfg/stk_markup_rules.json"
_MISSING_MSG = r"Filed to read vendor \(stk\) settings"
_PATHS = ParsePaths(file_prices_folder="/prices", user_config_folder="/cfg", result_folder="/prices/result")
_GET_PATHS = "parsers.data_provider.markup_rules.get_parse_paths"


def test_markup_rules_base() -> None:
    provider = MarkupRulesProviderBase("s1")
    assert provider.supplier_name == "s1"
    with pytest.raises(NotImplementedError):
        provider.get_markup_data()


def test_markup_path_with_supplier() -> None:
    provider = MarkupRulesProviderFromUserConfig("stk")
    with patch(_GET_PATHS, return_value=_PATHS):
        assert provider.get_file_path() == _STK_RULES_PATH


def test_markup_path_default() -> None:
    provider = MarkupRulesProviderFromUserConfig()
    with patch(_GET_PATHS, return_value=_PATHS):
        assert provider.get_file_path() == "/cfg/markup_rules.json"


def test_markup_missing_file() -> None:
    provider = MarkupRulesProviderFromUserConfig("stk")
    with (
        patch.object(CoreExceptionError, _TO_LOG),
        patch.object(provider, "get_file_path", return_value=_MISSING_FILE),
        patch(
            "parsers.data_provider.markup_rules.read_file",
            side_effect=FileNotFoundError,
        ) as mock_read,
        pytest.raises(PriceRulesConfigFileError, match=_MISSING_MSG),
    ):
        provider.get_markup_data()
    mock_read.assert_called_once_with(_MISSING_FILE)


def test_load_markup_reads_file_path() -> None:
    provider = MarkupRulesProviderFromUserConfig("stk")
    with (
        patch(_GET_PATHS, return_value=_PATHS),
        patch("parsers.data_provider.markup_rules.read_file", return_value="{}") as mock_read,
    ):
        assert provider.get_markup_data() == {}
        mock_read.assert_called_once_with(_STK_RULES_PATH)


def test_rule_defaults_when_keys_missing() -> None:
    markup = markup_params_from_rule({})
    assert markup == data_provider.MarkUpParams(min=0, max=0, percent_markup=0)


def test_rule_accepts_percent_key() -> None:
    markup = markup_params_from_rule({"min": 0, "max": 100, "percent": _PERCENT})
    assert markup == data_provider.MarkUpParams(min=0, max=100, percent_markup=_PERCENT)


def test_rule_accepts_percent_markup_key() -> None:
    markup = markup_params_from_rule({"min": 10, "max": _RULE_MAX, "percent_markup": _PERCENT_ALT})
    assert markup == data_provider.MarkUpParams(min=10, max=_RULE_MAX, percent_markup=_PERCENT_ALT)


def test_rule_prefers_percent_markup() -> None:
    markup = markup_params_from_rule(
        {"min": 0, "max": 1, "percent": 0.5, "percent_markup": _PREFERRED},
    )
    assert markup.percent_markup == pytest.approx(_PREFERRED)


_ZAPASKA_MIN_RECOMMENDED = 0.08
_ZAPASKA_DELTA = 150
_ZAPASKA_FIRST_MAX = 4999
_MODE_MULTIPLIER = "multiplier"
_MODE_DELTA = "delta"


def test_extract_optional_keys_default() -> None:
    rules = extract_markup_rules({"markup_rules": {}})
    assert rules.replace_small_recommended is False
    assert rules.absolute_markup_rules.mode == _MODE_MULTIPLIER
    assert rules.min_recommended_percent_markup == 0
    assert rules.max_recommended_percent_markup == 0


def test_extract_zero_cap_stays_zero() -> None:
    """Явный 0 в JSON — кап выключен, не fallback 1."""
    rules = extract_markup_rules(
        {
            "min_recommended_percent_markup": 0,
            "max_recommended_percent_markup": 0,
        },
    )
    assert rules.min_recommended_percent_markup == 0
    assert rules.max_recommended_percent_markup == 0


def test_extract_zapaska_policy_fields() -> None:
    rules = extract_markup_rules(
        {
            "markup_rules": {"r22": {"min": 0, "max": _ZAPASKA_FIRST_MAX, "percent": _PERCENT}},
            "replace_small_recommended": True,
            "min_recommended_percent_markup": _ZAPASKA_MIN_RECOMMENDED,
            "absolute_markup_rules": {
                "min_absolute_markup": _ZAPASKA_DELTA,
                "mode": _MODE_DELTA,
            },
        },
    )
    assert rules.replace_small_recommended is True
    assert rules.min_recommended_percent_markup == pytest.approx(_ZAPASKA_MIN_RECOMMENDED)
    assert rules.absolute_markup_rules.min_absolute_markup == _ZAPASKA_DELTA
    assert rules.absolute_markup_rules.mode == _MODE_DELTA
