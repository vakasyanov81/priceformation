"""StrategyHooks — точка интеграции стратегий в BaseParser (этап 3).

Хуки BaseParser, при наличии ``StrategyHooks``, делегируют стратегиям.
"""

from __future__ import annotations

from dataclasses import dataclass

from domain.protocols import ConfigProvider
from parsers.base_parser.warehouse_filter import CityWarehouseFilter
from parsers.strategies.category_fields import CategoryFields
from parsers.strategies.product_type import ProductTypeClassifier
from parsers.strategies.protocols import CategoryStrategy, RestStrategy, TitleStrategy
from parsers.vendor_config.slot_configs import DEFAULT_PIPELINE, BehaviorConfig


@dataclass(frozen=True, slots=True)
class StrategyHooks:
    """Стратегии и параметры поведения для config-driven парсера.

    Если поле ``None``, BaseParser использует дефолтную логику хука.
    """

    category: CategoryStrategy | None = None
    title: TitleStrategy | None = None
    rest: RestStrategy | None = None
    category_fields: CategoryFields | None = None
    product_type: ProductTypeClassifier | None = None
    min_rest: int = 4
    find_manufacturer_on_enrich: bool = True
    zero_rest_without_category: bool = False
    pipeline: tuple[str, ...] = DEFAULT_PIPELINE
    warehouse_filter: CityWarehouseFilter | None = None
    order_from_warehouse_name: bool = False


def warehouse_filter_for(
    behavior: BehaviorConfig, folder: str, config_provider: ConfigProvider
) -> CityWarehouseFilter | None:
    """Фильтр складов по городам, если они заданы в `behavior.warehouse_cities`."""
    if not behavior.warehouse_cities:
        return None
    return CityWarehouseFilter(folder=folder, cities=behavior.warehouse_cities, config_provider=config_provider)
