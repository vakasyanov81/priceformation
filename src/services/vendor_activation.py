"""Активация и деактивация поставщиков: список и переключение флага enabled."""

from dataclasses import dataclass

from parsers.vendor_config.provider import load_vendor_configs, set_vendor_enabled


@dataclass(frozen=True)
class VendorState:
    """Состояние поставщика: папка конфига, название и активность."""

    folder: str
    name: str
    enabled: bool


class VendorActivationService:
    """Читает список поставщиков и переключает их активность в конфиге."""

    def list_vendors(self) -> list[VendorState]:
        """Поставщики по названию с текущим флагом активности."""
        states: list[VendorState] = []
        for folder, config in load_vendor_configs().items():
            states.append(VendorState(folder, config.name, config.enabled))
        return sorted(states, key=lambda vendor: vendor.name)

    def toggle(self, folder: str) -> VendorState:
        """Инвертировать активность поставщика и сохранить в конфиг."""
        config = load_vendor_configs()[folder]
        enabled = not config.enabled
        set_vendor_enabled(folder, enabled)
        return VendorState(folder, config.name, enabled)
