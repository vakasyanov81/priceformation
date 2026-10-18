"""Загрузка данных поставщика «Форточки» через внешний API."""

from __future__ import annotations

from infrastructure.config.four_tochki_api_config import get_four_tochki_api_config
from parsers.remote.four_tochki_client import load_remote_vendor_data
from parsers.remote.four_tochki_warehouses import load_four_tochki_warehouse_groups


class FourTochkiService:
    """Выгрузка шин и дисков Форточек по API."""

    def upload_data(self) -> None:
        """Загрузить удалённые данные в file_prices/four_tochki."""
        load_remote_vendor_data(api=get_four_tochki_api_config(), groups=load_four_tochki_warehouse_groups())
