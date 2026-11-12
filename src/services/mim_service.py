"""Загрузка данных поставщика «МИМ» через внешний API."""

from __future__ import annotations

from domain.config_context import get_config_provider
from domain.protocols import ConfigProvider
from infrastructure.config.mim_api_config import get_mim_api_config
from infrastructure.remote.mim_client import MimApiRequest, load_remote_vendor_data, resolve_types
from parsers.vendor_config.group_models import TireAndDiskConfig
from parsers.vendor_config.provider import load_vendor_configs
from services.vendor_activity import skip_disabled_upload

_VENDOR_FOLDER = 'mim'


class MimService:
    """Выгрузка каталога МИМ по API."""

    def __init__(self, config_provider: ConfigProvider | None = None) -> None:
        self._config_provider = config_provider

    def upload_data(self) -> bool:
        """Загрузить удалённые данные в file_prices/mim; вернуть False, если поставщик отключён."""
        provider = self._config_provider or get_config_provider()
        if skip_disabled_upload(_VENDOR_FOLDER, provider):
            return False
        api = get_mim_api_config()
        types = resolve_types(_configured_types(provider))
        request = MimApiRequest(host=api.host, token=api.token, types=types)
        load_remote_vendor_data(api=request)
        return True


def _configured_types(config_provider: ConfigProvider) -> tuple[int, ...]:
    """Категории из `behavior.api_types` конфига МИМ; конфига нет — пусто (набор по умолчанию)."""
    config = load_vendor_configs(config_provider).get(_VENDOR_FOLDER)
    if config is not None:
        for group in config.product_groups:
            if isinstance(group, TireAndDiskConfig):
                return group.behavior.api_types
    return ()
