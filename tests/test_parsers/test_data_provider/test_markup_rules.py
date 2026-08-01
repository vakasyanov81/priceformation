"""tests for markup rules provider"""

from unittest.mock import patch

import pytest

from core.exceptions import CoreExceptionError
from parsers.data_provider.markup_rules import (
    MarkupRulesProviderBase,
    MarkupRulesProviderFromUserConfig,
    PriceRulesConfigFileError,
)

_TO_LOG = "to_log"


def test_markup_rules_base():
    provider = MarkupRulesProviderBase("s1")
    assert provider.supplier_name == "s1"
    with pytest.raises(NotImplementedError):
        provider.get_markup_data()


def test_markup_path_with_supplier():
    provider = MarkupRulesProviderFromUserConfig("stk")
    with patch("parsers.data_provider.markup_rules.MainConfig") as mock_cfg:
        mock_cfg.return_value.markup_rules_file_path = "/cfg/markup_rules.json"
        mock_cfg.return_value.markup_rules_file_name = "markup_rules.json"
        assert provider.get_file_path() == "/cfg/stk_markup_rules.json"


def test_markup_path_default():
    provider = MarkupRulesProviderFromUserConfig()
    with patch("parsers.data_provider.markup_rules.MainConfig") as mock_cfg:
        mock_cfg.return_value.markup_rules_file_path = "/cfg/markup_rules.json"
        assert provider.get_file_path() == "/cfg/markup_rules.json"


def test_markup_missing_file():
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
