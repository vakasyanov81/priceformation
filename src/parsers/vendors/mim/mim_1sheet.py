"""
logic for mim vendor (sheet 1)
"""

import dataclasses

from parsers.nomenclature_title import compose_tire_title, join_size_parts, load_velocity
from parsers.row_item.row_item import RowItem

from ...base_parser.base_parser_config import make_parse_config
from .mim_base import MimParserBase, mim_params

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

mim_sheet_1_config = make_parse_config(mim_sheet_1_params)


def is_number(candidate: str | int | float) -> bool:
    """value like xx.xx or xx.0"""
    try:
        return bool(float(candidate)) and "." in str(candidate)
    except ValueError:
        return False


class MimParser1Sheet(MimParserBase):
    """
    parser for mim vendor (sheet 1)
    """

    @classmethod
    def get_current_category(cls) -> str:
        return "Легковая шина"

    def get_prepared_title(self, row_item: RowItem) -> str:
        """get prepared title"""
        profile = row_item.height_percent or ""
        delimiter = "x" if is_number(profile) else "/"
        size = join_size_parts(row_item.width, delimiter, profile, "R", row_item.diameter)
        return compose_tire_title(row_item, size, load_velocity(row_item))
