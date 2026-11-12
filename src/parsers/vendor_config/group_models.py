"""Раздельные типизированные настройки товарных групп."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Literal

from domain.product_groups import ProductGroup
from parsers.vendor_config.battery_settings import BatterySettings
from parsers.vendor_config.row_selector import RowSelector
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
    """Маршрут и собственные настройки аккумуляторной секции."""

    id: str
    name: str
    start_row: int
    file_templates: tuple[str, ...]
    sheet_info: str = ''
    sheet_indexes: tuple[int, ...] = ()
    row_selector: RowSelector | None = None
    config_path: str = field(default='', compare=False, repr=False)
    columns: Mapping[int | str, str] = field(default_factory=lambda: MappingProxyType({}))
    processing: BatterySettings = field(default_factory=BatterySettings)

    @property
    def product_group(self) -> Literal[ProductGroup.BATTERIES]:
        """Маршрут не может быть использован как шинная секция."""
        return ProductGroup.BATTERIES


@dataclass(frozen=True, slots=True)
class BatteryConfig:
    """Настройки аккумуляторных секций с собственной моделью и обработкой."""

    sections: tuple[BatterySection, ...]

    @property
    def id(self) -> Literal[ProductGroup.BATTERIES]:
        """Идентификатор отдельной модели настроек."""
        return ProductGroup.BATTERIES


type GroupConfig = TireAndDiskConfig | BatteryConfig
