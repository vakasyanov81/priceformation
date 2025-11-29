"""Parse configuration"""

from parsers import data_provider
from parsers.base_parser.base_parser_config import BasePriceParseConfigurationParams
from test_parsers.test_vendors.test_parse_poshk import (
    BlackListProviderForTests,
    ManufacturerAliasesProviderForTests,
    MarkupRulesProviderForTests,
    StopWordsProviderForTests,
    VendorListProviderForTests,
    vendor_list_config,
)


def make_parse_configuration(parser_params, markup_rules=None):
    """make parse configuration"""
    return BasePriceParseConfigurationParams(
        black_list_provider=BlackListProviderForTests(),
        markup_rules_provider=markup_rules or MarkupRulesProviderForTests(),
        stop_words_provider=StopWordsProviderForTests(),
        vendor_list=VendorListProviderForTests(vendor_list_config),
        manufacturer_aliases=ManufacturerAliasesProviderForTests(),
        parser_params=parser_params,
    )


class MimMarkupRulesProviderForTests(data_provider.MarkupRulesProviderBase):
    """markup rules data provider for mim supplier tests"""

    def get_markup_data(self):
        """get markup rules"""
        return {
            "markup_rules": {
                "rule_70": {"min": 0, "max": 5001, "percent": 0.22},
                "rule_50": {"min": 5000, "max": 10001, "percent": 0.22},
                "rule_40": {"min": 10000, "max": 15001, "percent": 0.22},
                "rule_30": {"min": 15000, "max": 20001, "percent": 0.14},
                "rule_25": {"min": 20000, "max": 25001, "percent": 0.12},
            },
            "min_recommended_percent_markup": 0.14,
            "max_recommended_percent_markup": 0.27,
            "absolute_markup_rules": {
                "min_absolute_markup": 300,
                "markup_percent": 1.5,
            },
        }


class PionerMarkupRulesProviderForTests(data_provider.MarkupRulesProviderBase):
    """markup rules data provider for mim supplier tests"""

    @classmethod
    def get_markup_data(cls):
        """get markup rules"""
        return {
            "markup_rules": {
                "rule_70": {"min": 0, "max": 1000, "percent": 0.20},
                "rule_30": {"min": 1001, "max": 2000, "percent": 0.18},
                "rule_15": {"min": 5000, "max": 15000, "percent": 0.12},
                "rule_14": {"min": 15001, "max": 99999, "percent": 0.07},
                "rule_7": {"min": 100000, "max": 500000, "percent": 0.05},
            }
        }
