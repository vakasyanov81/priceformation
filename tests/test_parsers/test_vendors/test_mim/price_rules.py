# -*- coding: utf-8 -*-
"""
price rules for tests for mim vendor
"""
__author__ = "Kasyanov V.A."

from parsers import data_provider


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
                "min_absolute_markup": 200,
                "markup_percent": 1.5,
            },
        }
