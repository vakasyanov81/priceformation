"""Источник записей поставщиков для оркестратора: реестр конфигов + провайдер путей окружения."""

from domain.config_context import get_config_provider
from domain.protocols import ConfigProvider
from parsers.all_vendors import VendorEntry, all_vendors
from parsers.registry import vendor_entry_for
from parsers.vendor_config.reference_priority import load_reference_priority


class VendorSource:
    """Отдаёт записи поставщиков, передавая реестру провайдер путей окружения."""

    def __init__(self, config_provider: ConfigProvider | None = None) -> None:
        self._config_provider = config_provider

    def all(self) -> list[VendorEntry]:
        """Все поставщики из конфигов, включая отключённых."""
        return all_vendors(self._provider())

    def entry_for(self, code: str) -> VendorEntry:
        """Запись поставщика по коду (id секции)."""
        return vendor_entry_for(code, self._provider())

    def reference_priority(self) -> dict[str, int]:
        """Очередь поставщиков-эталонов названия из общих настроек."""
        return load_reference_priority(self._provider())

    def _provider(self) -> ConfigProvider:
        """Явно переданный провайдер или активный; активный берётся в момент вызова, а не создания сервиса."""
        return self._config_provider or get_config_provider()
