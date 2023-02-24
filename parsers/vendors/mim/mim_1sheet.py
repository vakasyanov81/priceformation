# -*- coding: utf-8 -*-
"""
logic for mim vendor (sheet 1)
"""
__author__ = "Kasyanov V.A."
from parsers.row_item.vendors.row_item_mim import RowItemMim

from .mim_base import MimParserBase


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

    __SUPPLIER_FOLDER_NAME__ = MimParserBase.__SUPPLIER_FOLDER_NAME__
    __COLUMNS__ = {
        0: RowItemMim.__CODE__,
        1: RowItemMim.__TITLE__,
        4: RowItemMim.__MANUFACTURER_NAME__,
        5: RowItemMim.__MODEL__,
        6: RowItemMim.__DIAMETER__,
        7: RowItemMim.__WIDTH__,
        8: RowItemMim.__PROFILE__,
        10: RowItemMim.__INDEX_VELOCITY__,
        11: RowItemMim.__INDEX_LOAD__,
        17: RowItemMim.__REST_COUNT__,
        19: RowItemMim.__PRICE_PURCHASE__,
        20: RowItemMim.__PRICE_RECOMMENDED__,
    }

    __SHEET_INFO__ = "Вкладка #1"

    __SHEET_INDEXES__ = [0]

    @classmethod
    def get_current_category(cls):
        return "Автошина"

    @classmethod
    def get_prepared_title(cls, item: RowItemMim):
        """get prepared title"""
        width = item.width or ""
        diameter = item.diameter or ""
        profile = item.profile or ""
        velocity = item.index_velocity or ""
        load = item.index_load or ""
        model = item.model or ""
        mark = (item.manufacturer or "").lower().capitalize()
        delimiter = "x" if is_number(profile) else "/"

        title = (
            f"{width}{delimiter}{profile}R{diameter} {mark} {model} {load}{velocity}"
        )

        return title
