"""StrategyHooks — точка интеграции стратегий в BaseParser (этап 3).

Хуки BaseParser, при наличии ``StrategyHooks``, делегируют стратегиям.
"""

from __future__ import annotations

from dataclasses import dataclass

from parsers.strategies.protocols import CategoryStrategy, RestStrategy, TitleStrategy
from parsers.vendor_config.slot_configs import DEFAULT_PIPELINE


@dataclass(frozen=True, slots=True)
class StrategyHooks:
    """Стратегии и параметры поведения для config-driven парсера.

    Если поле ``None``, BaseParser использует дефолтную логику хука.
    """

    category: CategoryStrategy | None = None
    title: TitleStrategy | None = None
    rest: RestStrategy | None = None
    min_rest: int = 4
    find_manufacturer_on_enrich: bool = True
    zero_rest_without_category: bool = False
    pipeline: tuple[str, ...] = DEFAULT_PIPELINE
