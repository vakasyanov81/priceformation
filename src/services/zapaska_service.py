"""Загрузка данных поставщика «Запаска» через внешний API."""

from __future__ import annotations

from domain.config_context import get_config_provider
from domain.protocols import ConfigProvider
from infrastructure.config.zapaska_api_config import get_zapaska_api_config
from infrastructure.remote.zapaska_client import load_remote_vendor_data
from services.vendor_activity import skip_disabled_upload

_VENDOR_FOLDER = 'zapaska'


class ZapaskaService:
    """Выгрузка прайсов запаски по API."""

    def __init__(self, config_provider: ConfigProvider | None = None) -> None:
        self._config_provider = config_provider

    def upload_data(self) -> None:
        """Загрузить удалённые данные в локальную базу."""
        if skip_disabled_upload(_VENDOR_FOLDER, self._config_provider or get_config_provider()):
            return
        load_remote_vendor_data(api=get_zapaska_api_config())
