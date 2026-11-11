"""Активация и деактивация поставщиков: список и переключение флага enabled."""

from dataclasses import dataclass

from domain.config_context import get_config_provider
from domain.product_groups import ProductGroup
from domain.protocols import ConfigProvider
from parsers.vendor_config.activation import set_vendor_enabled
from parsers.vendor_config.provider import load_vendor_configs


@dataclass(frozen=True)
class VendorState:
    """Состояние поставщика: папка конфига, название и активность."""

    folder: str
    name: str
    enabled: bool
    product_groups: tuple[ProductGroup, ...] = (ProductGroup.TIRE_AND_DISK,)


class VendorActivationService:
    """Читает список поставщиков и переключает их активность в конфиге."""

    def __init__(self, config_provider: ConfigProvider | None = None) -> None:
        self._config_provider = config_provider

    def list_vendors(self) -> list[VendorState]:
        """Поставщики по названию с текущим флагом активности."""
        states: list[VendorState] = []
        for folder, config in load_vendor_configs(self._provider()).items():
            groups = tuple(group.id for group in config.product_groups)
            states.append(VendorState(folder, config.name, config.enabled, groups))
        return sorted(states, key=lambda vendor: vendor.name)

    def toggle(self, folder: str) -> VendorState:
        """Инвертировать активность поставщика и сохранить в конфиг."""
        config = load_vendor_configs(self._provider())[folder]
        enabled = not config.enabled
        set_vendor_enabled(folder, enabled, self._provider())
        groups = tuple(group.id for group in config.product_groups)
        return VendorState(folder, config.name, enabled, groups)

    def _provider(self) -> ConfigProvider:
        """Явно переданный провайдер или активный в момент вызова."""
        return self._config_provider or get_config_provider()
