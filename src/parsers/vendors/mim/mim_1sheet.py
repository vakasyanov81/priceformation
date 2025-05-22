# -*- coding: utf-8 -*-
"""
logic for mim vendor (sheet 1)
"""
__author__ = "Kasyanov V.A."

import dataclasses

from src.parsers.row_item.row_item import RowItem
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
    0: RowItem.__CODE__,
    1: RowItem.__TITLE__,
    3: RowItem.__SEASON__,
    4: RowItem.__MANUFACTURER_NAME__,
    5: RowItem.__MODEL__,
    6: RowItem.__DIAMETER__,
    7: RowItem.__WIDTH__,
    8: RowItem.__PROFILE__,
    9: RowItem.__SPIKE__,
    10: RowItem.__INDEX_VELOCITY__,
    11: RowItem.__INDEX_LOAD__,
    17: RowItem.__REST_COUNT__,
    19: RowItem.__PRICE_PURCHASE__,
    20: RowItem.__PRICE_RECOMMENDED__,
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
        return "Легковая шина"

    @classmethod
    def get_prepared_title(cls, item: RowItem):
        """get prepared title"""
        width = item.width or ""
        diameter = item.diameter or ""
        profile = item.profile or ""
        velocity = item.index_velocity or ""
        load = item.index_load or ""
        model = item.model or ""
        mark = (item.manufacturer or "").lower().capitalize()
        delimiter = "x" if is_number(profile) else "/"

        title = f"{width}{delimiter}{profile}R{diameter} {mark} {model} {load}{velocity}"

        return title
