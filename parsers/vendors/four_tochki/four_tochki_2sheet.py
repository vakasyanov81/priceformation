# -*- coding: utf-8 -*-
"""
logic for four_tochki vendor (sheet 2)
"""
__author__ = "Kasyanov V.A."
from parsers.row_item.vendors.row_item_mim import RowItemMim as RowItem

from .four_tochki_base import FourTochkiParserBase


class FourTochkiParser2Sheet(FourTochkiParserBase):
    """
    parser for four_tochki vendor (sheet 2)
    """

    __SUPPLIER_FOLDER_NAME__ = FourTochkiParserBase.__SUPPLIER_FOLDER_NAME__
    __COLUMNS__ = {
        0: RowItem.__CODE__,
        1: RowItem.__MANUFACTURER_NAME__,
        2: RowItem.__MODEL__,
        3: RowItem.__WIDTH__,
        4: RowItem.__DIAMETER__,
        5: RowItem.__SLOT_COUNT__,
        6: RowItem.__PCD1__,
        8: RowItem.__ET__,
        9: RowItem.__CENTRAL_DIAMETER__,
        10: RowItem.__COLOR__,
        12: RowItem.__REST_COUNT__,
        13: RowItem.__PRICE_RECOMMENDED__,
        14: RowItem.__PRICE_PURCHASE__,
    }

    __SHEET_INFO__ = "Вкладка (диски) #2"

    __SHEET_INDEXES__ = [1]

    @classmethod
    def get_current_category(cls):
        return "Диск"

    @classmethod
    def get_prepared_title(cls, item: RowItem):
        width = item.width or ""
        diameter = item.diameter or ""
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
