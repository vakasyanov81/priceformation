"""Загрузка данных поставщика «Запаска» через внешний API."""

from __future__ import annotations

from cfg.zapaska_api import get_zapaska_api_config
from parsers.remote.zapaska_client import load_remote_vendor_data


class ZapaskaService:
    """Выгрузка прайсов запаски по API."""

    def upload_data(self) -> None:
        """Загрузить удалённые данные в локальную базу."""
        load_remote_vendor_data(api=get_zapaska_api_config())
