# -*- coding: utf-8 -*-
"""
logic for four_tochki vendor (sheet 2)
"""
__author__ = "Kasyanov V.A."

import dataclasses

from src.parsers.row_item.vendors.row_item_mim import RowItemMim as RowItem

from ... import data_provider
from ...base_parser.base_parser_config import (
    BasePriceParseConfigurationParams,
    ParseConfiguration,
)
from .four_tochki_1sheet import supplier_folder_name
from .four_tochki_base import FourTochkiParserBase, fourtochki_params

fourtochki_sheet_2_params = dataclasses.replace(fourtochki_params)
fourtochki_sheet_2_params.sheet_info = "Вкладка (шины) #2"
fourtochki_sheet_2_params.sheet_indexes = [1]
fourtochki_sheet_2_params.columns = {
    0: RowItem.__CODE__,
    1: RowItem.__MANUFACTURER_NAME__,
    2: RowItem.__MODEL__,
    3: RowItem.__WIDTH__,
    4: RowItem.__DIAMETER__,
    5: RowItem.__SLOT_COUNT__,
    6: RowItem.__PCD1__,
    8: RowItem.__ET__,
    9: RowItem.__CENTRAL_DIAMETER__,
    10: RowItem.__COLOR__,
    12: RowItem.__REST_COUNT__,
    13: RowItem.__PRICE_RECOMMENDED__,
    14: RowItem.__PRICE_PURCHASE__,
}


mark_up_provider = data_provider.MarkupRulesProviderFromUserConfig(supplier_folder_name)

fourtochki_sheet_2_config = BasePriceParseConfigurationParams(
    markup_rules_provider=mark_up_provider,
    black_list_provider=data_provider.BlackListProviderFromUserConfig(),
    stop_words_provider=data_provider.StopWordsProviderFromUserConfig(),
    vendor_list=data_provider.VendorListProviderFromUserConfig(),
    manufacturer_aliases=data_provider.ManufacturerAliasesProviderFromUserConfig(),
    parser_params=fourtochki_sheet_2_params,
)

fourtochki_sheet_2_config = ParseConfiguration(fourtochki_sheet_2_config)


class FourTochkiParser2Sheet(FourTochkiParserBase):
    """
    parser for four_tochki vendor (sheet 2)
    """

    @classmethod
    def get_current_category(cls, item):
        return "Диск"

    @classmethod
    def get_prepared_title(cls, item: RowItem):
        width = item.width or ""
        diameter = item.diameter or ""
        model = item.model or ""
        slot_count = item.slot_count or ""
        pcd1 = item.pcd1 or ""
        dia = item.central_diameter or ""
        color = item.color or ""
        _et = item.eet or ""
        mark = (item.manufacturer or "").lower().capitalize()

        # 6,5x16 5x114,3 ET45 60,1 MBMF Alcasta M35
        title = f"{width}x{diameter} {slot_count}x{pcd1} ET{_et} {dia} {color} {mark} {model}"

        return title
