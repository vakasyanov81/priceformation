"""tests for markup rules provider"""

from unittest.mock import patch

import pytest

from core.exceptions import CoreExceptionError
from parsers import data_provider
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


def test_markup_rules_base() -> None:
    provider = MarkupRulesProviderBase("s1")
    assert provider.supplier_name == "s1"
    with pytest.raises(NotImplementedError):
        provider.get_markup_data()


def test_markup_path_with_supplier() -> None:
    provider = MarkupRulesProviderFromUserConfig("stk")
    with patch("parsers.data_provider.markup_rules.MainConfig") as mock_cfg:
        mock_cfg.return_value.markup_rules_file_path = "/cfg/markup_rules.json"
        mock_cfg.return_value.markup_rules_file_name = "markup_rules.json"
        assert provider.get_file_path() == "/cfg/stk_markup_rules.json"


def test_markup_path_default() -> None:
    provider = MarkupRulesProviderFromUserConfig()
    with patch("parsers.data_provider.markup_rules.MainConfig") as mock_cfg:
        mock_cfg.return_value.markup_rules_file_path = "/cfg/markup_rules.json"
        assert provider.get_file_path() == "/cfg/markup_rules.json"


def test_markup_missing_file() -> None:
    provider = MarkupRulesProviderFromUserConfig("stk")
    with (
        patch.object(CoreExceptionError, _TO_LOG),
        patch.object(provider, "get_file_path", return_value="/no"),
        patch(
            "parsers.data_provider.markup_rules.read_file",
            side_effect=FileNotFoundError,
        ),
        pytest.raises(PriceRulesConfigFileError),
    ):
        provider.get_markup_data()


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
