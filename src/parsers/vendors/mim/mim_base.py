"""
base logic for mim vendor
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

mim_params = ParserParams(
    supplier=ParseParamsSupplier(folder_name="mim", name="Мим", code="4"),
    start_row=2,
    sheet_info="",
    columns={},
    stop_words=[],
    file_templates=["price*.xls", "price*.xlsx"],
    sheet_indexes=[],
    row_item_adaptor=RowItem,
)

supplier_folder_name = mim_params.supplier.folder_name


mark_up_provider = data_provider.MarkupRulesProviderFromUserConfig(supplier_folder_name)

mim_config = ParseConfiguration(
    BasePriceParseConfigurationParams(
        markup_rules_provider=mark_up_provider,
        black_list_provider=data_provider.BlackListProviderFromUserConfig(),
        stop_words_provider=data_provider.StopWordsProviderFromUserConfig(),
        vendor_list=data_provider.VendorListProviderFromUserConfig(),
        manufacturer_aliases=data_provider.ManufacturerAliasesProviderFromUserConfig(),
        parser_params=mim_params,
    )
)


class MimParserBase(MarkupSkipCategoryParser):
    """
    base logic for mim vendor
    """

    @classmethod
    def get_current_category(cls) -> str:
        """getting current category"""
        raise NotImplementedError()

    def set_category(self, row_item: RowItem) -> None:
        """set category to row price item"""
        row_item.type_production = self.get_current_category()
