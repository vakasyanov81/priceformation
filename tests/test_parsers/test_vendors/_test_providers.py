"""Тестовые провайдеры данных, общие для нескольких файлов тестов.

Выделено из ``test_parse_poshk.py``, чтобы разорвать зависимость от
``parsers.vendors``.
"""

from __future__ import annotations

from typing import Any

from test_base_parser.test_manufacturer_finder import map_manufacturer

from parsers import data_provider

_TEST_RULES_WHERE = 'test_markup_rules.json'


class MarkupRulesProviderForTests(data_provider.MarkupRulesProviderBase):
    """markup rules data provider for tests"""

    def get_markup_data(self) -> data_provider.MarkupRulesConfig:
        """get markup rules"""
        return data_provider.MarkupRulesConfig.from_dict(
            {
                'markup_rules': {
                    'rule_70': {'min': 0, 'max': 200, 'percent_markup': 0.7},
                    'rule_50': {'min': 200, 'max': 300, 'percent_markup': 0.5},
                    'rule_40': {'min': 300, 'max': 500, 'percent_markup': 0.4},
                    'rule_30': {'min': 500, 'max': 1500, 'percent_markup': 0.3},
                    'rule_25': {'min': 1500, 'max': 5000, 'percent_markup': 0.25},
                    'rule_15': {'min': 5000, 'max': 8000, 'percent_markup': 0.15},
                    'rule_14': {'min': 8000, 'max': 20000, 'percent_markup': 0.14},
                    'rule_8': {'min': 20000, 'max': 30000, 'percent_markup': 0.08},
                    'rule_7': {'min': 30000, 'max': 60000, 'percent_markup': 0.07},
                },
            },
            _TEST_RULES_WHERE,
        )


class ManufacturerAliasesProviderForTests(data_provider.ManufacturerAliasesProviderBase):
    """manufacturer aliases data provider for tests"""

    def get_aliases(self) -> dict[str, Any]:
        """get manufacturer aliases"""
        return dict(map_manufacturer)


class BlackListProviderForTests(data_provider.BlackListProviderBase):
    """black list data provider for tests"""

    def get_black_list_data(self) -> list[str]:
        """get black list"""
        return ['wrong title', 'wrong title 2']

    def get_stop_words_data(self) -> list[str]:
        """get glob masks (same as *lines* in black_list)"""
        return ['*некондиция*', '*2 сорт*', '*восстановленная*', 'брак*']
