"""
logic for zapaska (rest) vendor
"""

import traceback
from base64 import b64encode
from http.client import HTTPException, HTTPSConnection
from pathlib import Path

from cfg import init_cfg
from cfg.zapaska_api import ZapaskaApiConfig, ZapaskaApiConnectionError, get_zapaska_api_config

from ..base_parser.base_parser_config import (
    ParseParamsSupplier,
    ParserParams,
    make_parse_config,
)
from ..base_parser.category_finder import canonical_product_type, raw_category_label
from ..row_item.row_item import RowItem
from .zapaska_disk_json import ZapaskaDiskJSON, column_mapping

column_mapping = dict(column_mapping)
column_mapping.update(
    {
        "height": RowItem.height_percent.name,
        "load_index": RowItem.index_load.name,
        "speed_index": RowItem.index_velocity.name,
        "studded": RowItem.spike.name,
    }
)

zapaska_tire_params = ParserParams(
    supplier=ParseParamsSupplier(folder_name="zapaska", name="Запаска (шины)", code="22"),
    start_row=0,
    sheet_info="",
    columns=column_mapping,
    stop_words=[],
    file_templates=["tire.json"],
    sheet_indexes=[],
    row_item_adaptor=RowItem,
)

zapaska_tire_config = make_parse_config(zapaska_tire_params)


class ZapaskaTireJSON(ZapaskaDiskJSON):
    """
    Parser rest and price opt for zapaska vendor
    """

    _type_production = "Шины"

    def category_for(self, row_item: RowItem) -> str | None:
        """Map supplier category onto the allowed product types."""
        resolved = canonical_product_type(row_item.type_production, self._category_finder)
        if resolved:
            return resolved
        self.unknown_category_skips.append(raw_category_label(row_item.type_production))
        return ""


def basic_auth(username: str, password: str) -> str:
    """auth"""
    token = b64encode(f"{username}:{password}".encode()).decode("ascii")
    return f"Basic {token}"


def get_data(url: str, api_config: ZapaskaApiConfig | None = None) -> str:
    """GET from Zapaska API."""
    api_config = api_config or get_zapaska_api_config()
    try:
        return _request_zapaska(url, api_config)
    except (OSError, HTTPException) as exc:
        raise _zapaska_connection_error(url, api_config.host, exc) from exc


def _request_zapaska(url: str, api_config: ZapaskaApiConfig) -> str:
    """Perform GET against Zapaska HTTPS API."""
    connection = HTTPSConnection(api_config.host)
    headers = {"Authorization": basic_auth(api_config.login, api_config.password)}
    connection.request("GET", url, headers=headers)
    payload = connection.getresponse().read().decode("utf-8")
    connection.close()
    return payload


def _zapaska_connection_error(url: str, host: str, exc: Exception) -> ZapaskaApiConnectionError:
    """Human-readable connection error; original exception goes to logs."""
    detail = f"host={host} url={url}\n{exc!r}\n{traceback.format_exc()}"
    return ZapaskaApiConnectionError(detail=detail)


def save_data(json_data: str, filename: str) -> None:
    """save data to file"""
    main_cfg = init_cfg().main
    file_path = (
        Path(main_cfg.project_root) / main_cfg.folder_file_prices / zapaska_tire_params.supplier.folder_name / filename
    )
    with file_path.open("w", encoding="utf-8") as out_file:
        out_file.write(json_data)


def load_remote_data() -> None:
    """Скачать шины и диски Запаски в file_prices."""
    save_data(get_data("/API/hs/V2/GetTires"), filename="tire.json")
    save_data(get_data("/API/hs/V2/GetDisk"), filename="disk.json")
