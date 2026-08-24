"""
logic for mim vendor (sheet 1)
"""

import dataclasses

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

    @classmethod
    def get_prepared_title(cls, row_item: RowItem) -> str:
        """get prepared title"""
        profile = row_item.height_percent or ""
        delimiter = "x" if is_number(profile) else "/"
        mark = (row_item.manufacturer or "").lower().capitalize()
        return _mim1_title(row_item, profile, delimiter, mark)


def _mim1_title(row_item: RowItem, profile: str, delimiter: str, mark: str) -> str:
    """Собрать title легковой шины MIM sheet1."""
    width = row_item.width or ""
    diameter = row_item.diameter or ""
    size = f"{width}{delimiter}{profile}R{diameter}"
    return " ".join(
        (
            size,
            mark,
            row_item.model or "",
            "{}{}".format(row_item.index_load or "", row_item.index_velocity or ""),
        ),
    )
