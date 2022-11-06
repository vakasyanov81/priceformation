# -*- coding: utf-8 -*-
"""
logic for mim vendor (sheet 3)
"""
__author__ = "Kasyanov V.A."

from parsers.vendors.mim.mim_2sheet import config_for_sheets23
from .mim_base import MimParserBase


class MimParser3Sheet(MimParserBase):
    """
    parser for mim vendor (sheet 3)
    """
    __SUPPLIER_FOLDER_NAME__ = MimParserBase.__SUPPLIER_FOLDER_NAME__
    __COLUMNS__ = config_for_sheets23()

    __SHEET_INDEXES__ = [2]

    __SHEET_INFO__ = "Вкладка #3"

    @classmethod
    def get_current_category(cls):
        return "Диск"
