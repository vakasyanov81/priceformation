# -*- coding: utf-8 -*-
"""
logic for mim vendor (sheet 1)
"""
__author__ = "Kasyanov V.A."

import dataclasses

from parsers.row_item.vendors.row_item_mim import RowItemMim
from .mim_base import MimParserBase, mim_params, supplier_folder_name
from ... import data_provider
from ...base_parser.base_parser_config import (
    BasePriceParseConfigurationParams,
    ParseConfiguration,
)

mim_sheet_1_params = dataclasses.replace(mim_params)
mim_sheet_1_params.sheet_info = "Вкладка #1"
mim_sheet_1_params.sheet_indexes = [0]
mim_sheet_1_params.columns = {
    0: RowItemMim.__CODE__,
    1: RowItemMim.__TITLE__,
    4: RowItemMim.__MANUFACTURER_NAME__,
    5: RowItemMim.__MODEL__,
    6: RowItemMim.__DIAMETER__,
    7: RowItemMim.__WIDTH__,
    8: RowItemMim.__PROFILE__,
    10: RowItemMim.__INDEX_VELOCITY__,
    11: RowItemMim.__INDEX_LOAD__,
    17: RowItemMim.__REST_COUNT__,
    19: RowItemMim.__PRICE_PURCHASE__,
    20: RowItemMim.__PRICE_RECOMMENDED__,
}

mark_up_provider = data_provider.MarkupRulesProviderFromUserConfig(supplier_folder_name)

mim_sheet_1_config = BasePriceParseConfigurationParams(
    markup_rules_provider=mark_up_provider,
    black_list_provider=data_provider.BlackListProviderFromUserConfig(),
    stop_words_provider=data_provider.StopWordsProviderFromUserConfig(),
    vendor_list=data_provider.VendorListProviderFromUserConfig(),
    manufacturer_aliases=data_provider.ManufacturerAliasesProviderFromUserConfig(),
    parser_params=mim_sheet_1_params,
)

mim_sheet_1_config = ParseConfiguration(mim_sheet_1_config)


def is_number(value: str) -> bool:
    """value like xx.xx or xx.0"""
    try:
        return bool(float(value)) and "." in value
    except ValueError:
        return False


class MimParser1Sheet(MimParserBase):
    """
    parser for mim vendor (sheet 1)
    """

    @classmethod
    def get_current_category(cls):
        return "Автошина"

    @classmethod
    def get_prepared_title(cls, item: RowItemMim):
        """get prepared title"""
        width = item.width or ""
        diameter = item.diameter or ""
        profile = item.profile or ""
        velocity = item.index_velocity or ""
        load = item.index_load or ""
        model = item.model or ""
        mark = (item.manufacturer or "").lower().capitalize()
        delimiter = "x" if is_number(profile) else "/"

        title = (
            f"{width}{delimiter}{profile}R{diameter} {mark} {model} {load}{velocity}"
        )

        return title
