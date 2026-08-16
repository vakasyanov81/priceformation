"""
logic for autosnab54_ru vendor
"""

from parsers import data_provider
from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.base_parser_config import (
    BasePriceParseConfigurationParams,
    ParseConfiguration,
    ParseParamsSupplier,
    ParserParams,
)
from parsers.row_item.row_item import RowItem
from parsers.vendors.autosnab_title import fill_from_title

autosnab_params = ParserParams(
    supplier=ParseParamsSupplier(folder_name="autosnab54_ru", name="Автоснабжение", code="6"),
    start_row=2,
    sheet_info="",
    columns={
        0: RowItem.type_production.name,
        1: RowItem.manufacturer.name,
        2: RowItem.title.name,
        3: RowItem.season.name,
        4: RowItem.spike.name,
        5: RowItem.price_opt.name,
        6: RowItem.rest_count.name,
    },
    stop_words=[],
    file_templates=["price*.xls", "price*.xlsx"],
    sheet_indexes=[],
    row_item_adaptor=RowItem,
)


mark_up_provider = data_provider.MarkupRulesProviderFromUserConfig(autosnab_params.supplier.folder_name)

autosnab_config = ParseConfiguration(
    BasePriceParseConfigurationParams(
        markup_rules_provider=mark_up_provider,
        black_list_provider=data_provider.BlackListProviderFromUserConfig(),
        stop_words_provider=data_provider.StopWordsProviderFromUserConfig(),
        vendor_list=data_provider.VendorListProviderFromUserConfig(),
        manufacturer_aliases=data_provider.ManufacturerAliasesProviderFromUserConfig(),
        parser_params=autosnab_params,
    )
)


class Autosnab54Parser(BaseParser):
    """
    logic for autosnab54_ru vendor
    """

    def process(self) -> int:
        """parse process"""
        res = super().process()
        for row_item in self.parsed_items:
            fill_from_title(row_item)
            row_item.price_markup = row_item.price_opt

        return res

    @classmethod
    def get_min_rest_count(cls) -> int:
        """min rest count value for skip action"""
        return 0
