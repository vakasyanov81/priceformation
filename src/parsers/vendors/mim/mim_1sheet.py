"""
logic for mim vendor (sheet 1)
"""

import dataclasses

from parsers.row_item.row_item import RowItem

from ... import data_provider
from ...base_parser.base_parser_config import (
    BasePriceParseConfigurationParams,
    ParseConfiguration,
)
from .mim_base import MimParserBase, mim_params, supplier_folder_name

mim_sheet_1_params = dataclasses.replace(mim_params)
mim_sheet_1_params.sheet_info = "Вкладка #1"
mim_sheet_1_params.sheet_indexes = [0]
mim_sheet_1_params.columns = {
    0: RowItem.code.name,
    1: RowItem.title.name,
    3: RowItem.season.name,
    4: RowItem.manufacturer.name,
    5: RowItem.model.name,
    6: RowItem.diameter.name,
    7: RowItem.width.name,
    8: RowItem.height_percent.name,
    9: RowItem.spike.name,
    10: RowItem.index_velocity.name,
    11: RowItem.index_load.name,
    17: RowItem.rest_count.name,
    19: RowItem.price_opt.name,
    20: RowItem.price_recommended.name,
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


def is_number(value: str | int | float) -> bool:
    """value like xx.xx or xx.0"""
    try:
        return bool(float(value)) and "." in str(value)
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
        profile = item.height_percent or ""
        velocity = item.index_velocity or ""
        load = item.index_load or ""
        model = item.model or ""
        mark = (item.manufacturer or "").lower().capitalize()
        delimiter = "x" if is_number(profile) else "/"

        title = f"{width}{delimiter}{profile}R{diameter} {mark} {model} {load}{velocity}"

        return title
