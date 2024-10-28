# -*- coding: utf-8 -*-
"""
logic for four_tochki vendor (sheet 1)
"""
__author__ = "Kasyanov V.A."

import dataclasses

from parsers.row_item.vendors.row_item_mim import RowItemMim as RowItem

from ... import data_provider
from ...base_parser.base_parser_config import (
    BasePriceParseConfigurationParams,
    ParseConfiguration,
)
from .four_tochki_base import FourTochkiParserBase, fourtochki_params

fourtochki_sheet_1_params = dataclasses.replace(fourtochki_params)
fourtochki_sheet_1_params.sheet_info = "Вкладка (шины) #1"
fourtochki_sheet_1_params.sheet_indexes = [0]
fourtochki_sheet_1_params.columns = {
    0: RowItem.__CODE__,
    2: RowItem.__MANUFACTURER_NAME__,
    3: RowItem.__MODEL__,
    4: RowItem.__WIDTH__,
    5: RowItem.__HEIGHT_PERCENT__,
    6: RowItem.__DIAMETER__,
    7: RowItem.__INDEX_LOAD__,
    8: RowItem.__SEASON__,
    9: RowItem.__TIRE_TYPE__,
    10: RowItem.__EXT_DIAMETER__,
    11: RowItem.__SPIKE__,
    15: RowItem.__US_AFF_DESIGNATION__,
    17: RowItem.__REST_COUNT__,
    18: RowItem.__PRICE_RECOMMENDED__,
    19: RowItem.__PRICE_PURCHASE__,
}

supplier_folder_name = fourtochki_params.supplier.folder_name

mark_up_provider = data_provider.MarkupRulesProviderFromUserConfig(supplier_folder_name)

fourtochki_sheet_1_config = BasePriceParseConfigurationParams(
    markup_rules_provider=mark_up_provider,
    black_list_provider=data_provider.BlackListProviderFromUserConfig(),
    stop_words_provider=data_provider.StopWordsProviderFromUserConfig(),
    vendor_list=data_provider.VendorListProviderFromUserConfig(),
    manufacturer_aliases=data_provider.ManufacturerAliasesProviderFromUserConfig(),
    parser_params=fourtochki_sheet_1_params,
)

fourtochki_sheet_1_config = ParseConfiguration(fourtochki_sheet_1_config)


class FourTochkiParser1Sheet(FourTochkiParserBase):
    """
    parser for four_tochki vendor (sheet 1)
    """

    @classmethod
    def get_current_category(cls, item: RowItem):
        tyre_type_dict = {
            "грузовая": "Грузовая шина",
            "легковая": "Легковая шина",
            "спецтехника": "Спецшина",
            "мото": "Мотошина",
        }
        return tyre_type_dict.get(item.tire_type.lower().strip()) or "Автошина"

    def add_price_markup(self, item: RowItem):
        if item.price_recommended:
            price = item.price_recommended
        else:
            price_opt = item.price_opt or 0
            price = self.get_markup(price_opt, self.get_markup_percent(price_opt))
        item.price_markup = self.round_price(price)

    @classmethod
    def get_prepared_title(cls, item: RowItem):
        width = item.width or ""
        height_percent = item.height_percent or ""
        diameter = (item.diameter or "").replace("—", "-")
        velocity = item.index_velocity or ""
        load = item.index_load or ""
        model = item.model or ""
        ext_diameter = item.ext_diameter or ""
        us_aff_design = item.us_aff_design or ""
        mark = (item.manufacturer or "").lower().capitalize()
        construct = "R"
        if "-" in diameter:
            construct = "-"
            diameter = diameter.replace("-", "")

        # 205/55R16 BFGoodrich Advantage 94W
        # 30x9,5R15 BFGoodrich All Terrain T/A KO2 104S LT
        width_postfix = ".00"
        if diameter == "22.5" or height_percent:
            width_postfix = ""

        if cls.is_truck_tire(item) and diameter == "16":
            width_postfix = ""

        if height_percent:
            height_percent = f"/{height_percent}"
        else:
            height_percent = ""

        if cls.is_truck_tire(item):
            title = f"{width}{width_postfix}{height_percent}{construct}{diameter} {mark} {model} {load}{velocity}"
        elif ext_diameter:
            title = f"{ext_diameter}x{width}{construct}{diameter} {mark} {model} {load} {us_aff_design}"
        else:
            title = f"{width}{height_percent}{construct}{diameter} {mark} {model} {load}{velocity}"

        return title

    @classmethod
    def is_truck_tire(cls, item: RowItem):
        """Грузовая шина?"""
        return item.tire_type.lower() == "грузовая"
