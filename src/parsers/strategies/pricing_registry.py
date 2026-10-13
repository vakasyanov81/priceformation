"""
Реестр стратегий слота `pricing`: имя политики из конфига → политика наценки.
"""

from __future__ import annotations

from domain.exceptions import ConfigValidationError
from parsers.base_parser.markup_policy import (
    IdentityMarkupPolicy,
    MapOnOptMarkupPolicy,
    MarkupPolicy,
    RecommendedOrMapMarkupPolicy,
)
from parsers.strategies.pricing import PercentByThresholdMarkupPolicy, RecommendedRangeMarkupPolicy
from parsers.vendor_config.slot_configs import PricingConfig

_AVAILABLE = 'base, identity, map_on_opt, recommended_or_map, recommended_range, percent_by_threshold'

# Политики, которым правила `rules` и карта `%` передаются одинаково.
_RULE_POLICIES: dict[str, type[MarkupPolicy]] = {
    'base': MarkupPolicy,
    'map_on_opt': MapOnOptMarkupPolicy,
    'recommended_or_map': RecommendedOrMapMarkupPolicy,
    'recommended_range': RecommendedRangeMarkupPolicy,
}


def make_pricing_strategy(config: PricingConfig, where: str) -> MarkupPolicy:
    """Собрать политику наценки по слоту `pricing`."""
    rules = config.rules
    price_map = tuple(rules.markup_rules.values())
    if config.policy == 'percent_by_threshold':
        return PercentByThresholdMarkupPolicy(config.threshold, config.low, config.high)
    if config.policy == 'identity':
        return IdentityMarkupPolicy.create()
    policy_type = _RULE_POLICIES.get(config.policy)
    if policy_type is None:
        raise ConfigValidationError(
            f'{where}: неизвестная политика наценки {config.policy!r} (доступны: {_AVAILABLE})',
        )
    return policy_type(rules, price_map)
