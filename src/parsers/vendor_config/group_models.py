"""Раздельные типизированные настройки товарных групп."""

from dataclasses import dataclass
from typing import Literal

from domain.product_groups import ProductGroup
from parsers.vendor_config.section_models import VendorSection
from parsers.vendor_config.slot_configs import BehaviorConfig


@dataclass(frozen=True, slots=True)
class TireAndDiskConfig:
    """Разрешённые настройки текущей группы; аккумуляторных слотов здесь нет."""

    sections: tuple[VendorSection, ...]
    behavior: BehaviorConfig

    @property
    def id(self) -> Literal[ProductGroup.TIRE_AND_DISK]:
        """Идентификатор закреплён за моделью настроек и не передаётся снаружи."""
        return ProductGroup.TIRE_AND_DISK


@dataclass(frozen=True, slots=True)
class BatterySection:
    """Маршрут объявленной группы без ещё не определённых аккумуляторных полей."""

    id: str
    name: str
    start_row: int
    file_templates: tuple[str, ...]
    sheet_info: str = ''
    sheet_indexes: tuple[int, ...] = ()

    @property
    def product_group(self) -> Literal[ProductGroup.BATTERIES]:
        """Маршрут не может быть использован как шинная секция."""
        return ProductGroup.BATTERIES


@dataclass(frozen=True, slots=True)
class BatteryConfig:
    """Объявление аккумуляторов, не означающее готовность их обработчика."""

    sections: tuple[BatterySection, ...]

    @property
    def id(self) -> Literal[ProductGroup.BATTERIES]:
        """Идентификатор отдельной модели настроек."""
        return ProductGroup.BATTERIES


type GroupConfig = TireAndDiskConfig | BatteryConfig
