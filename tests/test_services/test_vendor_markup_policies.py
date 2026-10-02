"""tests for markup policies vendors get through ParseOrchestrator"""

from typing import Any, cast
from unittest.mock import patch

import pytest
from test_parsers.test_vendors import parse_config as vendor_parse_config

from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.base_parser_config import ParseConfiguration
from parsers.base_parser.markup_policy import (
    IdentityMarkupPolicy,
    MapOnOptMarkupPolicy,
    MarkupPolicy,
    RecommendedOrMapMarkupPolicy,
    percent_to_store,
)
from parsers.data_provider import MarkupRulesConfig, MarkupRulesProviderBase
from parsers.vendors.autosnab54_ru import Autosnab54Parser, autosnab_params
from parsers.vendors.four_tochki.four_tochki_sheet1 import FourTochkiParser1Sheet, fourtochki_sheet_1_params
from parsers.vendors.pioner import PionerParser, pioner_params
from parsers.vendors.poshk import PoshkParser, poshk_params
from parsers.vendors.stk import STKParser, stk_params
from services.parse_orchestrator import ParseOrchestrator


class _BoomMarkupRules(MarkupRulesProviderBase):
    def get_markup_data(self) -> MarkupRulesConfig:
        raise AssertionError('must not read markup rules')


def _markup_policy_from_parse_all(parser_cls: type[BaseParser], vendor_params: Any) -> MarkupPolicy:
    config = ParseConfiguration(vendor_parse_config.make_parse_configuration(vendor_params))
    orchestrator = ParseOrchestrator()
    with patch.object(orchestrator, '_parse_supplier') as mock_parse:
        orchestrator.parse_all([(parser_cls, config)])

    assert mock_parse.call_args is not None
    parser = mock_parse.call_args.args[1]
    return cast(MarkupPolicy, parser._row_processor._markup_policy)  # noqa: WPS437


@pytest.mark.parametrize(
    ('parser_cls', 'vendor_params'),
    [
        (PoshkParser, poshk_params),
        (PionerParser, pioner_params),
        (STKParser, stk_params),
    ],
)
def test_map_on_opt_vendors_get_map_policy(parser_cls: type[BaseParser], vendor_params: Any) -> None:
    assert isinstance(_markup_policy_from_parse_all(parser_cls, vendor_params), MapOnOptMarkupPolicy)


def test_autosnab_gets_identity_policy() -> None:
    assert isinstance(_markup_policy_from_parse_all(Autosnab54Parser, autosnab_params), IdentityMarkupPolicy)


def test_four_tochki_sheet1_rom_policy() -> None:
    assert isinstance(
        _markup_policy_from_parse_all(FourTochkiParser1Sheet, fourtochki_sheet_1_params),
        RecommendedOrMapMarkupPolicy,
    )


def test_autosnab_skips_markup_file() -> None:
    config = ParseConfiguration(
        vendor_parse_config.make_parse_configuration(autosnab_params, markup_rules=_BoomMarkupRules())
    )
    orchestrator = ParseOrchestrator()
    with patch.object(orchestrator, '_parse_supplier') as mock_parse:
        orchestrator.parse_all([(Autosnab54Parser, config)])

    assert mock_parse.call_args is not None
    parser = mock_parse.call_args.args[1]
    assert isinstance(parser._row_processor._markup_policy, IdentityMarkupPolicy)  # noqa: WPS437


def test_other_vendor_keeps_default_markup_policy() -> None:
    policy = _markup_policy_from_parse_all(BaseParser, pioner_params)
    assert percent_to_store(policy, 1000) is None
