"""
base parser config logic
"""

from dataclasses import dataclass
from typing import Any, NamedTuple

from domain.row_item.row_item import RowItem
from parsers import data_provider


class ParseConfigNotSetError(RuntimeError):
    """Raised when parse_config is not set on parser instance."""

    def __init__(self) -> None:
        super().__init__('parse_config is not set')


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
    vendor_list: data_provider.VendorListProviderBase
    manufacturer_aliases: data_provider.ManufacturerAliasesProviderBase
    parser_params: ParserParams


class ParseConfiguration:
    """base price parser configuration"""

    def __init__(self, parse_config: BasePriceParseConfigurationParams):
        """init"""
        self.parse_config: BasePriceParseConfigurationParams = parse_config
        self.parser_params = parse_config.parser_params
        self.supplier = self.parser_params.supplier
        self._markup_rules: data_provider.MarkupRulesConfig | None = None
        self._price_markup_map: tuple[data_provider.MarkUpRule, ...] | None = None
        self._all_vendor_config: dict[str, data_provider.VendorConfigEntry] | None = None
        self._manufacturer_aliases: dict[str, Any] | None = None

    def get_markup_rules(self) -> data_provider.MarkupRulesConfig:
        """get markup rules and caching"""
        if self._markup_rules is None:
            self._markup_rules = self.parse_config.markup_rules_provider.get_markup_data()
        return self._markup_rules

    def get_price_markup_map(self) -> tuple[data_provider.MarkUpRule, ...]:
        """get tuple with markup rules and caching"""
        if self._price_markup_map is None:
            self._price_markup_map = tuple(self.get_markup_rules().markup_rules.values())
        return self._price_markup_map

    def black_list(self) -> list[str]:
        """black list data"""
        return self.parse_config.black_list_provider.get_black_list_data()

    def stop_words(self) -> list[str]:
        """Glob masks from the black_list file (lines containing *)."""
        return self.parse_config.black_list_provider.get_stop_words_data()

    def manufacturer_aliases(self) -> dict[str, Any]:
        """manufacturer aliases data"""
        if self._manufacturer_aliases is None:
            self._manufacturer_aliases = self.parse_config.manufacturer_aliases.get_aliases()
        return self._manufacturer_aliases

    def all_vendor_config(self) -> dict[str, data_provider.VendorConfigEntry]:
        """config for all vendors"""
        if self._all_vendor_config is None:
            self._all_vendor_config = self.parse_config.vendor_list.get_config_vendor_list()
        return self._all_vendor_config


def make_parse_config(
    parser_params: ParserParams,
    *,
    markup_rules_provider: data_provider.MarkupRulesProviderBase | None = None,
    black_list_provider: data_provider.BlackListProviderBase | None = None,
    vendor_list: data_provider.VendorListProviderBase | None = None,
    manufacturer_aliases: data_provider.ManufacturerAliasesProviderBase | None = None,
) -> ParseConfiguration:
    """ParseConfiguration with default FromUserConfig providers."""
    folder_name = parser_params.supplier.folder_name
    return ParseConfiguration(
        BasePriceParseConfigurationParams(
            markup_rules_provider=markup_rules_provider or data_provider.MarkupRulesProviderFromUserConfig(folder_name),
            black_list_provider=black_list_provider or data_provider.BlackListProviderFromUserConfig(),
            vendor_list=vendor_list or data_provider.VendorListProviderFromUserConfig(),
            manufacturer_aliases=manufacturer_aliases or data_provider.ManufacturerAliasesProviderFromUserConfig(),
            parser_params=parser_params,
        )
    )
