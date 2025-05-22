# -*- coding: utf-8 -*-
"""
# если разница между оптовой и розничной ценой составляет меньше 200р
# то делаем наценку 15% к оптовой цене
# наценка не должна превышать 1000р
"""
__author__ = "Kasyanov V.A."

import dataclasses

from src.cfg import init_cfg
from src.parsers import data_provider
from src.parsers.base_parser.base_parser import BaseParser
from src.parsers.base_parser.base_parser_config import (
    BasePriceParseConfigurationParams,
    ParseConfiguration,
)
from src.parsers.row_item.row_item import RowItem
from src.parsers.vendors.zapaska_rest import (
    ZapaskaRestParser,
    zapaska_rest_config,
    zapaska_rest_params,
)
from http.client import HTTPSConnection
from base64 import b64encode

_SUPPLIER_FOLDER_NAME = "zapaska"
_SUPPLIER_NAME = "Запаска"
_SUPPLIER_CODE = "2"


zapaska_params = dataclasses.replace(zapaska_rest_params)
zapaska_params.columns = {
    0: RowItem.__CODE__,
    1: RowItem.__CODE_ART__,
    2: RowItem.__TITLE__,
    5: RowItem.__PRICE_RECOMMENDED__,
}
zapaska_params.start_row = 7
zapaska_params.supplier_name = _SUPPLIER_NAME
zapaska_params.file_templates = ["price*.xls", "price*.xlsx"]


mark_up_provider = data_provider.MarkupRulesProviderFromUserConfig(zapaska_params.supplier.folder_name)

zapaska_config = BasePriceParseConfigurationParams(
    markup_rules_provider=mark_up_provider,
    black_list_provider=data_provider.BlackListProviderFromUserConfig(),
    stop_words_provider=data_provider.StopWordsProviderFromUserConfig(),
    vendor_list=data_provider.VendorListProviderFromUserConfig(),
    manufacturer_aliases=data_provider.ManufacturerAliasesProviderFromUserConfig(),
    parser_params=zapaska_params,
)

zapaska_config = ParseConfiguration(zapaska_config)


# Authorization token: we need to base 64 encode it
# and then decode it to acsii as python 3 stores it as a byte string
def basic_auth(username, password):
    token = b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
    return f"Basic {token}"


def get_data(url: str) -> str:
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
    folder = init_cfg().main.folder_file_prices + "/" + zapaska_params.supplier.folder_name
    root = init_cfg().main.project_root
    with open(f"{root}/{folder}/{filename}", "w") as file_:
        file_.write(data)


def load_data():
    # save_data('{"d": 1}', filename="tire.json")
    save_data(get_data("/API/hs/V2/GetTires"), filename="tire.json")
    save_data(get_data("/API/hs/V2/GetDisk"), filename="disk.json")


class ZapaskaPriceAndRestParser:
    """
    combine price parser and rest parser
    """

    _parser = None

    def __init__(self, price_config=None):
        self.price_config = price_config

    def get_result(self):
        """get result"""
        if not ZapaskaRestParser.is_active:
            return []
        return ZapaskaRestParser(price_mrp=self.get_price_mrp(), parse_config=zapaska_rest_config).parse()

    def get_price_mrp(self):
        """get price mrp result"""
        return ZapaskaParser(parse_config=self.price_config).parse()

    @classmethod
    def supplier_folder_name(cls):
        return zapaska_params.supplier.folder_name

    def parse(self):
        return self.get_result()


class ZapaskaParser(BaseParser):
    """
    minimal recommended price
    """

    def after_process(self):
        pass
