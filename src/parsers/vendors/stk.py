"""
# stk
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

STK_START_ROW = 14
STK_PRICE_MARKUP_MULTIPLIER = 1.06

stk_params = ParserParams(
    supplier=ParseParamsSupplier(folder_name="stk", name="STK", code="7"),
    start_row=STK_START_ROW,
    sheet_info="",
    columns={
        1: RowItem.code.name,
        2: RowItem.title.name,
        3: RowItem.price_opt.name,
        4: RowItem.rest_count.name,
    },
    stop_words=[],
    file_templates=["price*.xls", "price*.xlsx"],
    sheet_indexes=[],
    row_item_adaptor=RowItem,
)


mark_up_provider = data_provider.MarkupRulesProviderFromUserConfig(stk_params.supplier.folder_name)

stk_config = ParseConfiguration(
    BasePriceParseConfigurationParams(
        markup_rules_provider=mark_up_provider,
        black_list_provider=data_provider.BlackListProviderFromUserConfig(),
        stop_words_provider=data_provider.StopWordsProviderFromUserConfig(),
        vendor_list=data_provider.VendorListProviderFromUserConfig(),
        manufacturer_aliases=data_provider.ManufacturerAliasesProviderFromUserConfig(),
        parser_params=stk_params,
    )
)


class STKParser(BaseParser):
    """
    parser for Greenstone vendor
    """

    def process(self) -> int:
        """process price parse"""
        res = super().process()
        for row_item in self.parsed_items:
            self.skip_by_min_rest(row_item)
            self.add_price_markup(row_item)

        return res

    def add_price_markup(self, row_item: RowItem) -> None:
        """
        Добавить наценку
        """

        if not row_item.price_opt:
            return
        row_item.price_markup = self.round_price(row_item.price_opt * STK_PRICE_MARKUP_MULTIPLIER)
