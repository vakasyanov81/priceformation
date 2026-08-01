"""
logic for zapaska (rest) vendor
"""

from base64 import b64encode
from http.client import HTTPSConnection
from pathlib import Path

from cfg import init_cfg
from cfg.zapaska_api import ZapaskaApiConfig, get_zapaska_api_config

from .. import data_provider
from ..base_parser.base_parser_config import (
    BasePriceParseConfigurationParams,
    ParseConfiguration,
    ParseParamsSupplier,
    ParserParams,
)
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

mark_up_provider = data_provider.MarkupRulesProviderFromUserConfig(zapaska_tire_params.supplier.folder_name)

zapaska_tire_config = BasePriceParseConfigurationParams(
    markup_rules_provider=mark_up_provider,
    black_list_provider=data_provider.BlackListProviderFromUserConfig(),
    stop_words_provider=data_provider.StopWordsProviderFromUserConfig(),
    vendor_list=data_provider.VendorListProviderFromUserConfig(),
    manufacturer_aliases=data_provider.ManufacturerAliasesProviderFromUserConfig(),
    parser_params=zapaska_tire_params,
)

zapaska_tire_config = ParseConfiguration(zapaska_tire_config)


class ZapaskaTireJSON(ZapaskaDiskJSON):
    """
    Parser rest and price opt for zapaska vendor
    """

    _type_production = "Шины"

    def get_type_production(self, item: RowItem):
        return item.type_production


def basic_auth(username, password):
    """auth"""
    token = b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
    return f"Basic {token}"


def get_data(url: str, api_config: ZapaskaApiConfig | None = None) -> str:
    """GET from Zapaska API."""
    api_config = api_config or get_zapaska_api_config()

    connection = HTTPSConnection(api_config.host)
    headers = {"Authorization": basic_auth(api_config.login, api_config.password)}
    connection.request("GET", url, headers=headers)
    res = connection.getresponse()
    return res.read().decode("utf-8")


def save_data(data: str, filename: str):
    """save data to file"""
    folder = init_cfg().main.folder_file_prices + "/" + zapaska_tire_params.supplier.folder_name
    root = init_cfg().main.project_root
    with Path(f"{root}/{folder}/{filename}").open("w", encoding="utf-8") as file_:
        file_.write(data)


def load_data():
    """load (tire / disk) data from file"""
    save_data(get_data("/API/hs/V2/GetTires"), filename="tire.json")
    save_data(get_data("/API/hs/V2/GetDisk"), filename="disk.json")
