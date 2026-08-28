"""
logic for four_tochki vendor (sheet 2)
"""

import dataclasses

from parsers.nomenclature_title import brand_label, join_size_parts, join_title_parts
from parsers.row_item.row_item import RowItem

from ...base_parser.base_parser_config import make_parse_config
from .four_tochki_base import FourTochkiParserBase, fourtochki_params
from .four_tochki_disk_title import (
    disk_diameter,
    disk_name_suffix,
    et_label,
    fill_disk_thickness,
)

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

fourtochki_sheet_2_config = make_parse_config(fourtochki_sheet_2_params)


class FourTochkiParser2Sheet(FourTochkiParserBase):
    """
    parser for four_tochki vendor (sheet 2)
    """

    @classmethod
    def get_current_category(cls, row_item: RowItem) -> str:
        return "Диск"

    def get_prepared_title(self, row_item: RowItem) -> str:
        original_name = row_item.title or ""
        fill_disk_thickness(row_item)
        return join_title_parts(
            _disk_title(row_item, disk_diameter(row_item.diameter)),
            disk_name_suffix(original_name),
        )


def _disk_title(row_item: RowItem, diameter: str) -> str:
    """Title диска: size bolts ET dia color mark model."""
    return join_title_parts(
        join_size_parts(row_item.width, "x", diameter),
        join_size_parts(row_item.slot_count, "x", row_item.pcd1),
        et_label(row_item.eet),
        row_item.central_diameter,
        row_item.color,
        brand_label(row_item),
        row_item.model,
    )
