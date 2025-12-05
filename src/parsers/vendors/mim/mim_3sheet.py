"""
logic for mim vendor (sheet 3)
"""

import dataclasses

from parsers.vendors.mim.mim_2sheet import mim_sheet_2_params
from .mim_base import MimParserBase, supplier_folder_name
from ... import data_provider
from ...base_parser.base_parser_config import (
    BasePriceParseConfigurationParams,
    ParseConfiguration,
)
from ...row_item.row_item import RowItem


def config_for_sheets3():
    """get config for sheets 3 parsers"""
    return dict(
        {
            0: RowItem.__CODE__,
            1: RowItem.__TITLE__,
            3: RowItem.__MANUFACTURER_NAME__,
            4: RowItem.__MODEL__,
            6: RowItem.__DIAMETER__,
            7: RowItem.__WIDTH__,
            8: RowItem.__SLOT_COUNT__,
            9: RowItem.__PCD1__,
            11: RowItem.__ET__,
            12: RowItem.__CENTRAL_DIAMETER__,
            15: RowItem.__DISK_THICKNESS__,
            20: RowItem.__REST_COUNT__,
            22: RowItem.__PRICE_PURCHASE__,
            23: RowItem.__PRICE_RECOMMENDED__,
        }
    )


mim_sheet_3_params = dataclasses.replace(mim_sheet_2_params)
mim_sheet_3_params.sheet_info = "Вкладка #3"
mim_sheet_3_params.sheet_indexes = [2]
mim_sheet_3_params.columns = config_for_sheets3()

mark_up_provider = data_provider.MarkupRulesProviderFromUserConfig(supplier_folder_name)

mim_sheet_3_config = BasePriceParseConfigurationParams(
    markup_rules_provider=mark_up_provider,
    black_list_provider=data_provider.BlackListProviderFromUserConfig(),
    stop_words_provider=data_provider.StopWordsProviderFromUserConfig(),
    vendor_list=data_provider.VendorListProviderFromUserConfig(),
    manufacturer_aliases=data_provider.ManufacturerAliasesProviderFromUserConfig(),
    parser_params=mim_sheet_3_params,
)

mim_sheet_3_config = ParseConfiguration(mim_sheet_3_config)


class MimParser3Sheet(MimParserBase):
    """
    parser for mim vendor (sheet 3)
    """

    @classmethod
    def get_current_category(cls):
        return "Диск"
