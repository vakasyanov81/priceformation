"""
# stk
"""

from parsers import data_provider
from parsers.base_parser.base_parser import MarkupSkipCategoryParser
from parsers.base_parser.base_parser_config import (
    BasePriceParseConfigurationParams,
    ParseConfiguration,
    ParseParamsSupplier,
    ParserParams,
)
from parsers.row_item.row_item import RowItem

STK_START_ROW = 14

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


class STKParser(MarkupSkipCategoryParser):
    """
    parser for Greenstone vendor
    """
