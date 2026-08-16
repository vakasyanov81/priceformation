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
from .four_tochki_disk_title import (
    disk_diameter,
    disk_name_suffix,
    et_label,
    fill_disk_thickness,
    join_title_parts,
)
from .four_tochki_sheet1 import supplier_folder_name

fourtochki_sheet_2_params = dataclasses.replace(fourtochki_params)
fourtochki_sheet_2_params.sheet_info = "Вкладка (диски) #2"
fourtochki_sheet_2_params.sheet_indexes = [1]
fourtochki_sheet_2_params.columns = {
    0: RowItem.code.name,
    1: RowItem.title.name,
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

fourtochki_sheet_2_config = ParseConfiguration(
    BasePriceParseConfigurationParams(
        markup_rules_provider=mark_up_provider,
        black_list_provider=data_provider.BlackListProviderFromUserConfig(),
        stop_words_provider=data_provider.StopWordsProviderFromUserConfig(),
        vendor_list=data_provider.VendorListProviderFromUserConfig(),
        manufacturer_aliases=data_provider.ManufacturerAliasesProviderFromUserConfig(),
        parser_params=fourtochki_sheet_2_params,
    )
)


class FourTochkiParser2Sheet(FourTochkiParserBase):
    """
    parser for four_tochki vendor (sheet 2)
    """

    @classmethod
    def get_current_category(cls, row_item: RowItem) -> str:
        return "Диск"

    @classmethod
    def get_prepared_title(cls, row_item: RowItem) -> str:
        original_name = row_item.title or ""
        fill_disk_thickness(row_item)
        mark = (row_item.manufacturer or "").lower().capitalize()
        return join_title_parts(
            _disk_title(row_item, mark, disk_diameter(row_item.diameter)),
            disk_name_suffix(original_name),
        )


def _disk_title(row_item: RowItem, mark: str, diameter: str) -> str:
    """Title диска: size bolts ET dia color mark model."""
    size = "x".join((str(row_item.width or ""), diameter))
    slot_count = str(row_item.slot_count or "")
    pcd1 = str(row_item.pcd1 or "")
    bolts = "x".join((slot_count, pcd1))
    return join_title_parts(
        size,
        bolts,
        et_label(row_item.eet),
        str(row_item.central_diameter or ""),
        str(row_item.color or ""),
        mark,
        str(row_item.model or ""),
    )
