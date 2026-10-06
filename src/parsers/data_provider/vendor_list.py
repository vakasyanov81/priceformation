"""Stub: vendor_list provider — replaced by ``vendors/*.json`` configs.

Сохраняется только для обратной совместимости тестов (этап 6 удалит).
"""

from parsers.data_provider.models import VendorConfigEntry


class VendorListProviderBase:
    """Base data provider with supplier config (deprecated)."""

    def get_config_vendor_list(self) -> dict[str, VendorConfigEntry]:
        """Abstract method. Get config for vendor list."""
        raise NotImplementedError


class VendorListProviderFromUserConfig(VendorListProviderBase):
    """Stub: читает vendor_list.json (deprecated — больше не используется)."""

    def get_config_vendor_list(self) -> dict[str, VendorConfigEntry]:
        """return empty — информация о включении теперь в vendors/*.json"""
        return {}
