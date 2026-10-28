"""Загрузка данных поставщика «Запаска» через внешний API."""

from __future__ import annotations

from infrastructure.config.zapaska_api_config import get_zapaska_api_config
from infrastructure.remote.zapaska_client import load_remote_vendor_data
from services.vendor_activity import skip_disabled_upload

_VENDOR_FOLDER = 'zapaska'


class ZapaskaService:
    """Выгрузка прайсов запаски по API."""

    def upload_data(self) -> None:
        """Загрузить удалённые данные в локальную базу."""
        if skip_disabled_upload(_VENDOR_FOLDER):
            return
        load_remote_vendor_data(api=get_zapaska_api_config())
