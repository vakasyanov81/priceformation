# -*- coding: utf-8 -*-
"""
base parser logic
"""
__author__ = "Kasyanov V.A."

from .manufacturer_aliases import ManufacturerAliasesProviderBase, ManufacturerAliasesProviderFromUserConfig
from .markup_rules import (
    MarkupRulesProviderBase,
    MarkupRulesProviderFromUserConfig,
    MarkupRules,
    AbsoluteMarkUpRules,
    MarkUpParams

)
from .black_list import BlackListProviderBase, BlackListProviderFromUserConfig
from .stop_words import StopWordsProviderBase, StopWordsProviderFromUserConfig
from .vendor_list import VendorListProviderBase, VendorListProviderFromUserConfig, VendorParams

__ALL__ = [
    ManufacturerAliasesProviderBase,
    ManufacturerAliasesProviderFromUserConfig,
    MarkupRulesProviderBase,
    MarkupRules,
    AbsoluteMarkUpRules,
    MarkUpParams,
    MarkupRulesProviderFromUserConfig,
    BlackListProviderBase,
    BlackListProviderFromUserConfig,
    StopWordsProviderBase,
    StopWordsProviderFromUserConfig,
    VendorListProviderBase,
    VendorListProviderFromUserConfig,
    VendorParams
]
