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
from parsers.strategies.pricing import PercentByThresholdMarkupPolicy
from parsers.vendor_config.slot_configs import PricingConfig

_AVAILABLE = 'base, identity, map_on_opt, recommended_or_map, percent_by_threshold'


def make_pricing_strategy(config: PricingConfig, where: str) -> MarkupPolicy:
    """Собрать политику наценки по слоту `pricing`."""
    rules = config.rules
    price_map = tuple(rules.markup_rules.values())
    if config.policy == 'base':
        return MarkupPolicy(rules, price_map)
    if config.policy == 'map_on_opt':
        return MapOnOptMarkupPolicy(rules, price_map)
    if config.policy == 'recommended_or_map':
        return RecommendedOrMapMarkupPolicy(rules, price_map)
    if config.policy == 'percent_by_threshold':
        return PercentByThresholdMarkupPolicy(config.threshold, config.low, config.high)
    if config.policy == 'identity':
        return IdentityMarkupPolicy.create()
    raise ConfigValidationError(
        f'{where}: неизвестная политика наценки {config.policy!r} (доступны: {_AVAILABLE})',
    )
