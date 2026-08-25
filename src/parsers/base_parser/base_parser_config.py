"""
base parser config logic
"""

from dataclasses import dataclass
from typing import Any, NamedTuple, cast

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
    stop_words: list[str]
    file_templates: list[str]
    sheet_indexes: list[int]
    row_item_adaptor: type[RowItem]


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
    raw_absolute = markup_data.get("absolute_markup_rules") or {}
    return data_provider.MarkupRules(
        markup_rules=cast(dict[str, dict[str, Any]], raw_rules),
        min_recommended_percent_markup=float(markup_data.get("min_recommended_percent_markup") or 0),
        max_recommended_percent_markup=float(markup_data.get("max_recommended_percent_markup") or 0),
        absolute_markup_rules=data_provider.AbsoluteMarkUpRules(**raw_absolute),
        replace_small_recommended=bool(markup_data.get("replace_small_recommended")),
    )


class ParseConfiguration:
    """base price parser configuration"""

    def __init__(self, parse_config: BasePriceParseConfigurationParams):
        """init"""
        self.parse_config: BasePriceParseConfigurationParams = parse_config
        self._markup_rules: data_provider.MarkupRules | None = None
        self._price_markup_map: tuple[data_provider.MarkUpParams, ...] | None = None
        self._all_vendor_config: dict[str, data_provider.VendorParams] | None = None
        self._manufacturer_aliases: dict[str, Any] | None = None

    def get_markup_rules(self) -> data_provider.MarkupRules:
        """get markup rules and caching"""
        if self._markup_rules is None:
            markup_data = self.parse_config.markup_rules_provider.get_markup_data() or {}
            self._markup_rules = extract_markup_rules(markup_data)
        return self._markup_rules

    def get_price_markup_map(self) -> tuple[data_provider.MarkUpParams, ...]:
        """get tuple with markup params and caching"""
        if self._price_markup_map is None:
            raw_rules = list(self.get_markup_rules().markup_rules.values())
            mapped_rules = [data_provider.markup_params_from_rule(rule) for rule in raw_rules]
            self._price_markup_map = tuple(mapped_rules)
        return self._price_markup_map

    def black_list(self) -> list[str]:
        """black list data"""
        return self.parse_config.black_list_provider.get_black_list_data()

    def stop_words(self) -> list[str]:
        """stop words data"""
        return self.parse_config.stop_words_provider.get_stop_words_data()

    def manufacturer_aliases(self) -> dict[str, Any]:
        """manufacturer aliases data"""
        if self._manufacturer_aliases is None:
            self._manufacturer_aliases = self.parse_config.manufacturer_aliases.get_aliases()
        return self._manufacturer_aliases

    def all_vendor_config(self) -> dict[str, data_provider.VendorParams]:
        """config for all vendors"""
        if self._all_vendor_config is None:
            vendor_config = self.parse_config.vendor_list.get_config_vendor_list()
            config = {}
            for vendor_name, raw_vendor_config in vendor_config.items():
                config[vendor_name] = data_provider.VendorParams(**raw_vendor_config)
            self._all_vendor_config = config
        return self._all_vendor_config


def _provider_or_default[ProviderT](provider: ProviderT | None, default: ProviderT) -> ProviderT:
    """Keep an explicit provider, otherwise use the factory default."""
    if provider is None:
        return default
    return provider


def make_parse_config(
    parser_params: ParserParams,
    *,
    markup_rules_provider: data_provider.MarkupRulesProviderBase | None = None,
    black_list_provider: data_provider.BlackListProviderBase | None = None,
    stop_words_provider: data_provider.StopWordsProviderBase | None = None,
    vendor_list: data_provider.VendorListProviderBase | None = None,
    manufacturer_aliases: data_provider.ManufacturerAliasesProviderBase | None = None,
) -> ParseConfiguration:
    """ParseConfiguration with default FromUserConfig providers."""
    folder_name = parser_params.supplier.folder_name
    return ParseConfiguration(
        BasePriceParseConfigurationParams(
            markup_rules_provider=_provider_or_default(
                markup_rules_provider,
                data_provider.MarkupRulesProviderFromUserConfig(folder_name),
            ),
            black_list_provider=_provider_or_default(
                black_list_provider,
                data_provider.BlackListProviderFromUserConfig(),
            ),
            stop_words_provider=_provider_or_default(
                stop_words_provider,
                data_provider.StopWordsProviderFromUserConfig(),
            ),
            vendor_list=_provider_or_default(
                vendor_list,
                data_provider.VendorListProviderFromUserConfig(),
            ),
            manufacturer_aliases=_provider_or_default(
                manufacturer_aliases,
                data_provider.ManufacturerAliasesProviderFromUserConfig(),
            ),
            parser_params=parser_params,
        )
    )
