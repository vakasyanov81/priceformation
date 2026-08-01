"""
base parser config logic
"""

from dataclasses import dataclass
from typing import Any, Dict, List, NamedTuple, Type, cast

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
    columns: dict[Any, str]
    stop_words: List[str]
    file_templates: List[str]
    sheet_indexes: List[int]
    row_item_adaptor: Type[RowItem]


class BasePriceParseConfigurationParams(NamedTuple):
    """container with parameters for instance PriceParser"""

    markup_rules_provider: data_provider.MarkupRulesProviderBase
    black_list_provider: data_provider.BlackListProviderBase
    stop_words_provider: data_provider.StopWordsProviderBase
    vendor_list: data_provider.VendorListProviderBase
    manufacturer_aliases: data_provider.ManufacturerAliasesProviderBase
    parser_params: ParserParams


def extract_markup_rules(markup_data: dict[str, Any]) -> data_provider.MarkupRules:
    """dict -> named tuple"""
    raw_rules = markup_data.get("markup_rules") or {}
    return data_provider.MarkupRules(
        markup_rules=cast(dict[str, dict[str, Any]], raw_rules),
        min_recommended_percent_markup=float(markup_data.get("min_recommended_percent_markup") or 0),
        max_recommended_percent_markup=float(markup_data.get("max_recommended_percent_markup") or 0),
        absolute_markup_rules=data_provider.AbsoluteMarkUpRules(**markup_data.get("absolute_markup_rules", {})),
    )


class ParseConfiguration:
    """base price parser configuration"""

    _markup_rules: data_provider.MarkupRules | None = None
    _price_markup_map: tuple[data_provider.MarkUpParams, ...] | None = None

    def __init__(self, parse_config: BasePriceParseConfigurationParams):
        """init"""
        self.parse_config: BasePriceParseConfigurationParams = parse_config
        self._all_vendor_config: Dict[str, data_provider.VendorParams] | None = None

    def get_markup_rules(self) -> data_provider.MarkupRules:
        """get markup rules and caching"""
        if not self._markup_rules:
            markup_data = self.parse_config.markup_rules_provider.get_markup_data() or {}
            self._markup_rules = extract_markup_rules(markup_data)
        return self._markup_rules

    def get_price_markup_map(self) -> tuple[data_provider.MarkUpParams, ...]:
        """get tuple with markup params and caching"""
        if not self._price_markup_map:
            raw_rules = list(self.get_markup_rules().markup_rules.values())
            mapped_rules = [data_provider.markup_params_from_rule(rule) for rule in raw_rules]
            self._price_markup_map = tuple(mapped_rules)
        return self._price_markup_map

    def black_list(self) -> List[str]:
        """black list data"""
        return self.parse_config.black_list_provider.get_black_list_data()

    def stop_words(self) -> List[str]:
        """stop words data"""
        return self.parse_config.stop_words_provider.get_stop_words_data()

    def manufacturer_aliases(self) -> dict[str, Any]:
        """manufacturer aliases data"""
        return self.parse_config.manufacturer_aliases.get_aliases()

    def all_vendor_config(self) -> Dict[str, data_provider.VendorParams]:
        """config for all vendors"""
        if self._all_vendor_config is None:
            vendor_config = self.parse_config.vendor_list.get_config_vendor_list()
            config = {}
            for vendor_name, raw_vendor_config in vendor_config.items():
                config[vendor_name] = data_provider.VendorParams(**raw_vendor_config)
            self._all_vendor_config = config
        return self._all_vendor_config
