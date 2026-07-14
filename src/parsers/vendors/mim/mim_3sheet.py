"""
logic for mim vendor (sheet 3)
"""

import dataclasses

from parsers.vendors.mim.mim_2sheet import mim_sheet_2_params

from ... import data_provider
from ...base_parser.base_parser_config import (
    BasePriceParseConfigurationParams,
    ParseConfiguration,
)
from ...row_item.row_item import RowItem
from .mim_base import MimParserBase, supplier_folder_name


def config_for_sheets3():
    """get config for sheets 3 parsers"""
    return dict(
        {
            0: RowItem.code.name,
            1: RowItem.title.name,
            3: RowItem.manufacturer.name,
            4: RowItem.model.name,
            6: RowItem.diameter.name,
            7: RowItem.width.name,
            8: RowItem.slot_count.name,
            9: RowItem.pcd1.name,
            11: RowItem.eet.name,
            12: RowItem.central_diameter.name,
            15: RowItem.disk_thickness.name,
            20: RowItem.rest_count.name,
            22: RowItem.price_opt.name,
            23: RowItem.price_recommended.name,
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
