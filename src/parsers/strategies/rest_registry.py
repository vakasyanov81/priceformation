"""
Реестр стратегий слота `rest`: имя из конфига → правило остатка.
"""

from __future__ import annotations

from domain.exceptions import ConfigValidationError
from parsers.strategies.protocols import RestStrategy
from parsers.strategies.rest import CountRest, MinusReserveRest
from parsers.vendor_config.slot_configs import BehaviorConfig

_AVAILABLE = 'count, minus_reserve'
_REST_STRATEGIES: dict[str, type[RestStrategy]] = {
    'count': CountRest,
    'minus_reserve': MinusReserveRest,
}


def make_rest_strategy(config: BehaviorConfig, where: str) -> RestStrategy:
    """Собрать стратегию остатка по секции `behavior`."""
    factory = _REST_STRATEGIES.get(config.rest)
    if factory is None:
        raise ConfigValidationError(
            f'{where}: неизвестная стратегия rest {config.rest!r} (доступны: {_AVAILABLE})',
        )
    return factory()
