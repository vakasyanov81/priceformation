# -*- coding: utf-8 -*-
"""
logic for zapaska (rest) vendor
"""
__author__ = "Kasyanov V.A."

from base64 import b64encode
from http.client import HTTPSConnection

from cfg import init_cfg
from .zapaska_disk_json import ZapaskaDiskJSON, column_mapping
from .. import data_provider
from ..base_parser.base_parser_config import (
    ParserParams,
    ParseParamsSupplier,
    BasePriceParseConfigurationParams,
    ParseConfiguration,
)

from ..row_item.row_item import RowItem

column_mapping = dict(column_mapping)
column_mapping.update(
    {
        "height": RowItem.__HEIGHT_PERCENT__,
        "load_index": RowItem.__INDEX_LOAD__,
        "speed_index": RowItem.__INDEX_VELOCITY__,
        "studded": RowItem.__SPIKE__,
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


# Authorization token: we need to base 64 encode it
# and then decode it to acsii as python 3 stores it as a byte string
def basic_auth(username, password):
    """auth"""
    token = b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
    return f"Basic {token}"


def get_data(url: str) -> str:
    """get data from ulr api"""
    api_cfg = mark_up_provider.get_markup_data().get("api")
    username = api_cfg.get("login")
    password = api_cfg.get("password")

    # This sets up the https connection
    connection = HTTPSConnection("ka2.sibzapaska.ru:16500")
    # then connect
    headers = {"Authorization": basic_auth(username, password)}
    connection.request("GET", url, headers=headers)
    # get the response back
    res = connection.getresponse()
    return res.read().decode("utf-8")


def save_data(data: str, filename: str):
    """save data to file"""
    folder = init_cfg().main.folder_file_prices + "/" + zapaska_tire_params.supplier.folder_name
    root = init_cfg().main.project_root
    with open(f"{root}/{folder}/{filename}", "w", encoding="utf-8") as file_:
        file_.write(data)


def load_data():
    """load (tire / disk) data from file"""
    # save_data('{"d": 1}', filename="tire.json")
    save_data(get_data("/API/hs/V2/GetTires"), filename="tire.json")
    save_data(get_data("/API/hs/V2/GetDisk"), filename="disk.json")
