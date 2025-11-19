# -*- coding: utf-8 -*-
"""
logic for zapaska (rest) vendor
"""
__author__ = "Kasyanov V.A."

from base64 import b64encode
from http.client import HTTPSConnection

from src.cfg import init_cfg
from .zapaska_disk_json import ZapaskaDiskJSON
from .. import data_provider
from ..base_parser.base_parser_config import (
    ParserParams,
    ParseParamsSupplier,
    BasePriceParseConfigurationParams,
    ParseConfiguration,
)

from ..row_item.row_item import RowItem

zapaska_tire_params = ParserParams(
    supplier=ParseParamsSupplier(folder_name="zapaska", name="Запаска (шины)", code="22"),
    start_row=0,
    sheet_info="",
    columns={
        RowItem.__CODE__: RowItem.__CODE__,
        "cae": RowItem.__CODE_ART__,
        "rest": RowItem.__REST_COUNT__,
        "price": RowItem.__PRICE_PURCHASE__,
        "retail": RowItem.__PRICE_RECOMMENDED__,
        "diam_center": RowItem.__CENTRAL_DIAMETER__,
        "holes": RowItem.__SLOT_COUNT__,
        "diam_holes": RowItem.__SLOT_DIAMETER__,
        "ET": RowItem.__ET__,
        "height": RowItem.__HEIGHT_PERCENT__,
        "load_index": RowItem.__INDEX_LOAD__,
        "speed_index": RowItem.__INDEX_VELOCITY__,
        "name": RowItem.__TITLE__,
        "category": RowItem.__TYPE_PRODUCTION__,
        "studded": RowItem.__SPIKE__,
    },
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

    @classmethod
    def get_prepared_title_new(cls, item: RowItem):
        """get prepared title"""
        width = (item.width or "").replace(".0", "")
        height_percent = str(item.height_percent or "")
        height_percent = height_percent.replace("999", "L")
        diameter = (item.diameter or "").replace("—", "-")
        # need for 4tochki vendor
        diameter = str(diameter).replace("R", "")
        velocity = item.index_velocity or ""
        load = item.index_load or ""
        model = item.model or ""
        brand = item.brand or ""
        ext_diameter = item.ext_diameter or ""
        us_aff_design = item.us_aff_design or ""
        mark = (item.manufacturer or "").lower().capitalize()
        layering = item.layering or ""
        camera_type = item.camera_type or ""
        construct = "R"
        if "-" in diameter:
            construct = "-"
            diameter = diameter.replace("-", "")

        # 205/55R16 BFGoodrich Advantage 94W
        # 30x9,5R15 BFGoodrich All Terrain T/A KO2 104S LT
        width_postfix = ""
        if cls.is_truck_tire(item):
            width_postfix = ".00"
        if diameter == "22.5" or height_percent:
            width_postfix = ""
        if cls.is_truck_tire(item) and diameter == "16":
            width_postfix = ""
        if width == "10" and diameter == "20":
            width_postfix = ".00"

        if cls.is_special_tire(item) and height_percent and height_percent != "L" and "." not in width:
            width_postfix = ".0"

        if height_percent == "L":
            width_postfix = height_percent

        if height_percent and height_percent != "L":
            height_percent = f"/{height_percent}"
        else:
            height_percent = ""

        construct_diameter = f"{construct}{diameter}"
        construct_diameter = construct_diameter.replace("RZ", "ZR")

        if cls.is_truck_tire(item):
            title = (
                f"{width}{width_postfix}{height_percent}{construct_diameter} {brand} {mark} {model} {load}{velocity}"
            )
        elif ext_diameter:
            title = f"{ext_diameter}x{width}{construct_diameter} {brand} {mark} {model} {load} {us_aff_design}"
        else:
            title = f"{width}{width_postfix}{height_percent}{construct_diameter} {brand} {mark} {model} {layering} {camera_type} {load}{velocity}"

        return title.strip()

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
