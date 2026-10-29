"""Загрузка данных поставщика «Форточки» через внешний API."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from domain.config_context import get_config_provider
from domain.four_tochki import FourTochkiWarehouseGroup
from domain.protocols import ConfigProvider
from infrastructure.config.four_tochki_api_config import FourTochkiApiConfig, get_four_tochki_api_config
from infrastructure.remote.four_tochki_client import download_catalogs, fetch_warehouses
from parsers.remote.four_tochki_warehouse_selection import log_selected_warehouses, select_warehouses
from parsers.remote.four_tochki_warehouses import load_four_tochki_warehouse_groups
from services.vendor_activity import skip_disabled_upload

_VENDOR_FOLDER = 'four_tochki'


def load_remote_vendor_data(*, api: FourTochkiApiConfig, groups: Sequence[FourTochkiWarehouseGroup]) -> None:
    """Подобрать склады API по группам, вывести их и выгрузить шины и диски в file_prices/four_tochki."""
    warehouses = select_warehouses(groups, fetch_warehouses(api))
    log_selected_warehouses(groups, warehouses)
    dest_dir = Path(get_config_provider().price_folder(_VENDOR_FOLDER))
    download_catalogs(dest_dir=dest_dir, api=api, warehouses=warehouses)


class FourTochkiService:
    """Выгрузка шин и дисков Форточек по API."""

    def __init__(self, config_provider: ConfigProvider | None = None) -> None:
        self._config_provider = config_provider

    def upload_data(self) -> None:
        """Загрузить удалённые данные в file_prices/four_tochki."""
        provider = self._config_provider or get_config_provider()
        if skip_disabled_upload(_VENDOR_FOLDER, provider):
            return
        load_remote_vendor_data(api=get_four_tochki_api_config(), groups=load_four_tochki_warehouse_groups(provider))
