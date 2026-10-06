"""
base parser logic
"""

from .black_list import BlackListProviderBase, BlackListProviderFromUserConfig
from .manufacturer_aliases import (
    ManufacturerAliasesProviderBase,
    ManufacturerAliasesProviderFromUserConfig,
)
from .markup_rules import MarkupRulesProviderBase, MarkupRulesProviderFromUserConfig
from .models import (
    ABSOLUTE_MODE_DELTA,
    ABSOLUTE_MODE_MULTIPLIER,
    AbsoluteMarkUpRules,
    MarkUpRule,
    MarkupRulesConfig,
    VendorConfigEntry,
)
from .title_aliases import TitleAliasesProviderBase, TitleAliasesProviderFromUserConfig

__all__ = [
    'ABSOLUTE_MODE_DELTA',
    'ABSOLUTE_MODE_MULTIPLIER',
    'AbsoluteMarkUpRules',
    'BlackListProviderBase',
    'BlackListProviderFromUserConfig',
    'ManufacturerAliasesProviderBase',
    'ManufacturerAliasesProviderFromUserConfig',
    'MarkUpRule',
    'MarkupRulesConfig',
    'MarkupRulesProviderBase',
    'MarkupRulesProviderFromUserConfig',
    'TitleAliasesProviderBase',
    'TitleAliasesProviderFromUserConfig',
    'VendorConfigEntry',
]
