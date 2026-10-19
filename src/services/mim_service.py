"""Загрузка данных поставщика «МИМ» через внешний API."""

from __future__ import annotations

from infrastructure.config.mim_api_config import get_mim_api_config
from parsers.remote.mim_client import load_remote_vendor_data


class MimService:
    """Выгрузка каталога МИМ по API."""

    def upload_data(self) -> None:
        """Загрузить удалённые данные в file_prices/mim."""
        load_remote_vendor_data(api=get_mim_api_config())
