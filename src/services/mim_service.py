"""Загрузка данных поставщика «МИМ» через внешний API."""

from __future__ import annotations

from infrastructure.config.mim_api_config import get_mim_api_config
from parsers.remote.mim_client import MimApiRequest, load_remote_vendor_data, resolve_types
from parsers.vendor_config.provider import load_vendor_configs
from services.vendor_activity import skip_disabled_upload

_VENDOR_FOLDER = 'mim'


class MimService:
    """Выгрузка каталога МИМ по API."""

    def upload_data(self) -> None:
        """Загрузить удалённые данные в file_prices/mim."""
        if skip_disabled_upload(_VENDOR_FOLDER):
            return
        api = get_mim_api_config()
        types = resolve_types(_configured_types())
        request = MimApiRequest(host=api.host, token=api.token, types=types)
        load_remote_vendor_data(api=request)


def _configured_types() -> tuple[int, ...]:
    """Категории из `behavior.api_types` конфига МИМ; конфига нет — пусто (набор по умолчанию)."""
    config = load_vendor_configs().get(_VENDOR_FOLDER)
    return config.behavior.api_types if config else ()
