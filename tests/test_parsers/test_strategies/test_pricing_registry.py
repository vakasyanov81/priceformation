"""Реестр стратегий pricing: имя политики → политика наценки."""

import pytest

from domain.exceptions import ConfigValidationError
from parsers.base_parser.markup_policy import (
    IdentityMarkupPolicy,
    MapOnOptMarkupPolicy,
    MarkupPolicy,
    RecommendedOrMapMarkupPolicy,
)
from parsers.data_provider.models import MarkUpRule, MarkupRulesConfig
from parsers.strategies.pricing import PercentByThresholdMarkupPolicy
from parsers.strategies.pricing_registry import make_pricing_strategy
from parsers.vendor_config.slot_configs import PricingConfig

WHERE = 'mim.json → sections[1] → pricing'

_KNOWN = [
    ('base', MarkupPolicy),
    ('identity', IdentityMarkupPolicy),
    ('map_on_opt', MapOnOptMarkupPolicy),
    ('recommended_or_map', RecommendedOrMapMarkupPolicy),
    ('percent_by_threshold', PercentByThresholdMarkupPolicy),
]


@pytest.mark.parametrize(('name', 'expected_type'), _KNOWN)
def test_make_known_pricing_strategy(name: str, expected_type: type) -> None:
    policy = make_pricing_strategy(PricingConfig(policy=name), WHERE)

    assert isinstance(policy, expected_type)


def test_map_on_opt_uses_rules_from_config() -> None:
    rule = MarkUpRule(min=0, max=5000, percent_markup=0.2)
    rules = MarkupRulesConfig(markup_rules={'r': rule})
    policy = make_pricing_strategy(PricingConfig(policy='map_on_opt', rules=rules), WHERE)

    assert policy.apply(1000, None) == pytest.approx(1200)


def test_threshold_uses_low_below_threshold() -> None:
    policy = PercentByThresholdMarkupPolicy(threshold=13000, low=0.07, high=0.05)

    assert policy.apply(10000, None) == pytest.approx(10700)


def test_threshold_uses_low_on_boundary() -> None:
    policy = PercentByThresholdMarkupPolicy(threshold=13000, low=0.07, high=0.05)

    assert policy.apply(13000, None) == pytest.approx(13910)


def test_threshold_uses_high_above_threshold() -> None:
    policy = PercentByThresholdMarkupPolicy(threshold=13000, low=0.07, high=0.05)

    assert policy.apply(20000, None) == pytest.approx(21000)


def test_threshold_without_opt_uses_low() -> None:
    policy = PercentByThresholdMarkupPolicy(threshold=13000, low=0.07, high=0.05)

    assert policy.apply(0, None) == pytest.approx(0)


def test_unknown_policy_raises_with_location() -> None:
    with pytest.raises(ConfigValidationError, match='неизвестная политика наценки'):
        make_pricing_strategy(PricingConfig(policy='nope'), WHERE)
