"""
base parser config logic
"""

from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, List, NamedTuple, Tuple, Type

from parsers import data_provider
from parsers.row_item.row_item import RowItem


@dataclass
class ParseParamsSupplier:
    """suppler params"""

    folder_name: str
    name: str
    code: str


@dataclass
class ParserParams:
    """parser params"""

    supplier: ParseParamsSupplier
    start_row: int
    sheet_info: str
    columns: dict
    stop_words: List[str]
    file_templates: List[str]
    sheet_indexes: List
    row_item_adaptor: Type[RowItem]


class BasePriceParseConfigurationParams(NamedTuple):
    """container with parameters for instance PriceParser"""

    markup_rules_provider: data_provider.MarkupRulesProviderBase
    black_list_provider: data_provider.BlackListProviderBase
    stop_words_provider: data_provider.StopWordsProviderBase
    vendor_list: data_provider.VendorListProviderBase
    manufacturer_aliases: data_provider.ManufacturerAliasesProviderBase
    parser_params: ParserParams


class ParseConfiguration:
    """base price parser configuration"""

    _markup_rules: data_provider.MarkupRules = None
    _price_markup_map: Tuple[data_provider.MarkUpParams] = None

    def __init__(self, parse_config: Type[BasePriceParseConfigurationParams]) -> None:
        """init"""
        self.parse_config: Type[BasePriceParseConfigurationParams] = parse_config

    @classmethod
    def extract_markup_rules(cls, markup_data: dict):
        """dict -> named tuple"""
        return data_provider.MarkupRules(
            markup_rules=markup_data.get("markup_rules"),
            min_recommended_percent_markup=markup_data.get("min_recommended_percent_markup"),
            max_recommended_percent_markup=markup_data.get("max_recommended_percent_markup"),
            absolute_markup_rules=data_provider.AbsoluteMarkUpRules(**markup_data.get("absolute_markup_rules", {})),
        )

    def get_markup_rules(self):
        """get markup rules and caching"""
        if not self._markup_rules:
            _data = self.parse_config.markup_rules_provider.get_markup_data() or {}
            self._markup_rules = self.extract_markup_rules(_data)
        return self._markup_rules

    def get_price_markup_map(self) -> Tuple[data_provider.MarkUpParams]:
        """get tuple with markup params and caching"""
        if not self._price_markup_map:
            _price_markup_map = list(self.get_markup_rules().markup_rules.values())
            _price_markup_map = [data_provider.MarkUpParams(**rule) for rule in _price_markup_map]
            self._price_markup_map = tuple(_price_markup_map)
        return self._price_markup_map

    def get_default_markup_percents(self, def_value=0.0) -> float:
        """get default (minimal) markup percent"""
        return min({item.percent for item in self.get_price_markup_map()} or (def_value,))

    def black_list(self) -> List[str]:
        """black list data"""
        return self.parse_config.black_list_provider.get_black_list_data()

    def stop_words(self) -> List[str]:
        """stop words data"""
        return self.parse_config.stop_words_provider.get_stop_words_data()

    def manufacturer_aliases(self) -> dict:
        """manufacturer aliases data"""
        return self.parse_config.manufacturer_aliases.get_aliases()

    @lru_cache()
    def all_vendor_config(self) -> Dict[str, data_provider.VendorParams]:
        """config for all vendors"""
        vendor_config = self.parse_config.vendor_list.get_config_vendor_list()
        config = {}
        for vendor_name, _vendor_config in vendor_config.items():
            config[vendor_name] = data_provider.VendorParams(**_vendor_config)
        return config
