"""
base parser logic
"""

from .black_list import BlackListProviderBase, BlackListProviderFromUserConfig
from .manufacturer_aliases import (
    ManufacturerAliasesProviderBase,
    ManufacturerAliasesProviderFromUserConfig,
)
from .markup_rules import (
    AbsoluteMarkUpRules,
    MarkUpParams,
    MarkupRules,
    MarkupRulesProviderBase,
    MarkupRulesProviderFromUserConfig,
    markup_params_from_rule,
)
from .stop_words import StopWordsProviderBase, StopWordsProviderFromUserConfig
from .vendor_list import (
    VendorListProviderBase,
    VendorListProviderFromUserConfig,
    VendorParams,
)

__all__ = [
    "ManufacturerAliasesProviderBase",
    "ManufacturerAliasesProviderFromUserConfig",
    "MarkupRulesProviderBase",
    "MarkupRules",
    "AbsoluteMarkUpRules",
    "MarkUpParams",
    "markup_params_from_rule",
    "MarkupRulesProviderFromUserConfig",
    "BlackListProviderBase",
    "BlackListProviderFromUserConfig",
    "StopWordsProviderBase",
    "StopWordsProviderFromUserConfig",
    "VendorListProviderBase",
    "VendorListProviderFromUserConfig",
    "VendorParams",
]
