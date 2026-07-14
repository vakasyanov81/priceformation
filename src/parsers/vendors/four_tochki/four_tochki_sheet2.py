"""
logic for four_tochki vendor (sheet 2)
"""

import dataclasses

from parsers.row_item.row_item import RowItem

from ... import data_provider
from ...base_parser.base_parser_config import (
    BasePriceParseConfigurationParams,
    ParseConfiguration,
)
from .four_tochki_base import FourTochkiParserBase, fourtochki_params
from .four_tochki_sheet1 import supplier_folder_name

fourtochki_sheet_2_params = dataclasses.replace(fourtochki_params)
fourtochki_sheet_2_params.sheet_info = "Вкладка (диски) #2"
fourtochki_sheet_2_params.sheet_indexes = [1]
fourtochki_sheet_2_params.columns = {
    0: RowItem.code.name,
    2: RowItem.manufacturer.name,
    3: RowItem.model.name,
    4: RowItem.color.name,
    5: RowItem.width.name,
    6: RowItem.diameter.name,
    7: RowItem.slot_count.name,
    8: RowItem.pcd1.name,
    9: RowItem.pcd2.name,
    10: RowItem.eet.name,
    11: RowItem.central_diameter.name,
    12: RowItem.fastener.name,
    13: RowItem.disk_type.name,
    14: RowItem.disk_type_1.name,
    15: RowItem.main_color.name,
    18: RowItem.rest_count.name,
    19: RowItem.price_recommended.name,
    20: RowItem.price_opt.name,
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
        diameter = (item.diameter or "").replace(".0", "")
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
