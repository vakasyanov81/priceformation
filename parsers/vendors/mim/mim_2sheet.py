# -*- coding: utf-8 -*-
"""
logic for mim vendor (sheet 2)
"""
__author__ = "Kasyanov V.A."
from parsers.row_item.vendors.row_item_mim import RowItemMim

from .mim_base import MimParserBase


def config_for_sheets23():
    """get config for sheets 2, 3 parsers"""
    return dict(
        {
            0: RowItemMim.__CODE__,
            1: RowItemMim.__TITLE__,
            3: RowItemMim.__MANUFACTURER_NAME__,
            4: RowItemMim.__MODEL__,
            6: RowItemMim.__WIDTH__,
            7: RowItemMim.__PROFILE__,
            8: RowItemMim.__CONSTRUCTION_TYPE__,
            9: RowItemMim.__DIAMETER__,
            11: RowItemMim.__AXIS__,
            12: RowItemMim.__INTIMACY__,
            13: RowItemMim.__LAYERING__,
            14: RowItemMim.__INDEX_LOAD__,
            15: RowItemMim.__INDEX_VELOCITY__,
            20: RowItemMim.__REST_COUNT__,
            22: RowItemMim.__PRICE_PURCHASE__,
            23: RowItemMim.__PRICE_RECOMMENDED__,
        }
    )


class MimParser2Sheet(MimParserBase):
    """
    parser for mim vendor (sheet 2)
    """

    __SUPPLIER_FOLDER_NAME__ = MimParserBase.__SUPPLIER_FOLDER_NAME__
    __COLUMNS__ = config_for_sheets23()

    __SHEET_INDEXES__ = [1]

    __SHEET_INFO__ = "Вкладка #2"

    @classmethod
    def get_current_category(cls):
        """current category"""
        return "Шина"

    @classmethod
    def get_prepared_title(cls, item: RowItemMim):
        """prepare title"""
        width = item.width or ""
        diameter = item.diameter or ""
        profile = item.profile or ""
        velocity = item.index_velocity or ""
        load = item.index_load or ""
        mark = (item.manufacturer or "").lower().capitalize()
        model = item.model or ""
        axis = item.axis or ""
        layering = item.layering or ""
        intimacy = item.intimacy or ""

        if profile:
            profile = f"/{profile}"

        if diameter:
            diameter = f"R{diameter}"

        chunks = [
            f"{width}{profile}{diameter}",
            mark,
            model,
            axis,
            layering,
            f"{load}{velocity}",
            intimacy,
        ]

        chunks = [str(chunk or "").strip() or None for chunk in chunks]

        chunks = [chunk for chunk in chunks if chunk]

        title = " ".join(chunks)

        return title
