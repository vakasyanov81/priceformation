# -*- coding: utf-8 -*-
"""
logic for mim vendor (sheet 3)
"""
__author__ = "Kasyanov V.A."

import dataclasses

from src.parsers.vendors.mim.mim_2sheet import mim_sheet_2_params

from ... import data_provider
from ...base_parser.base_parser_config import (
    BasePriceParseConfigurationParams,
    ParseConfiguration,
)
from .mim_base import MimParserBase, supplier_folder_name

mim_sheet_3_params = dataclasses.replace(mim_sheet_2_params)
mim_sheet_3_params.sheet_info = "Вкладка #3"
mim_sheet_3_params.sheet_indexes = [2]

mark_up_provider = data_provider.MarkupRulesProviderFromUserConfig(supplier_folder_name)

mim_sheet_3_config = BasePriceParseConfigurationParams(
    markup_rules_provider=mark_up_provider,
    black_list_provider=data_provider.BlackListProviderFromUserConfig(),
    stop_words_provider=data_provider.StopWordsProviderFromUserConfig(),
    vendor_list=data_provider.VendorListProviderFromUserConfig(),
    manufacturer_aliases=data_provider.ManufacturerAliasesProviderFromUserConfig(),
    parser_params=mim_sheet_3_params,
)

mim_sheet_3_config = ParseConfiguration(mim_sheet_3_config)


class MimParser3Sheet(MimParserBase):
    """
    parser for mim vendor (sheet 3)
    """

    @classmethod
    def get_current_category(cls):
        return "Диск"
