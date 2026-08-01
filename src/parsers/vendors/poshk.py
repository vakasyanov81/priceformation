"""
logic for posh vendor
"""

import re

from parsers import data_provider
from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.base_parser_config import (
    BasePriceParseConfigurationParams,
    ParseConfiguration,
    ParseParamsSupplier,
    ParserParams,
)
from parsers.row_item.row_item import RowItem

POSHK_START_ROW = 14
RE_PART_SIZE_PATTERN = r"^\d+\.*\d*"
RE_R_DIAMETER_PATTERN = r"R\d+."

poshk_params = ParserParams(
    supplier=ParseParamsSupplier(folder_name="poshk", name="Пошк", code="1"),
    start_row=POSHK_START_ROW,
    sheet_info="",
    columns={
        0: RowItem.code.name,
        1: RowItem.title.name,
        2: RowItem.price_opt.name,
        3: RowItem.rest_count.name,
    },
    stop_words=[],
    file_templates=["price*.xls", "price*.xlsx"],
    sheet_indexes=[],
    row_item_adaptor=RowItem,
)


mark_up_provider = data_provider.MarkupRulesProviderFromUserConfig(poshk_params.supplier.folder_name)

poshk_config = ParseConfiguration(
    BasePriceParseConfigurationParams(
        markup_rules_provider=mark_up_provider,
        black_list_provider=data_provider.BlackListProviderFromUserConfig(),
        stop_words_provider=data_provider.StopWordsProviderFromUserConfig(),
        vendor_list=data_provider.VendorListProviderFromUserConfig(),
        manufacturer_aliases=data_provider.ManufacturerAliasesProviderFromUserConfig(),
        parser_params=poshk_params,
    )
)


class PoshkParser(BaseParser):
    """
    logic for posh vendor
    """

    def process(self) -> int:
        """process price parse"""
        res = super().process()
        for row_item in self.parsed_items:
            self.add_price_markup(row_item)
            self.clear_and_set_title(row_item)
            row_item.title = self.prepare_title(row_item.title)
            self.set_type_production(row_item)

        return res

    def add_price_markup(self, row_item: RowItem) -> None:
        """
        Добавить наценку
        """

        price = row_item.price_opt
        markup_percent = self.get_markup_percent(price)
        price = (markup_percent + 1) * price
        row_item.price_markup = self.round_price(price)
        row_item.percent_markup = markup_percent * 100

    def set_type_production(self, row_item: RowItem) -> None:
        """
        Задать категорию
        """

        row_item.type_production = self.get_category_by_title(row_item.title)

    @classmethod
    def get_category_by_title(cls, title: str) -> str:
        """get category name by title"""
        title = title.lower()
        available_categories = ["ободная лента", "шина", "покрышка", "камера", "диск"]

        categories_map = {
            available_categories[0]: "Ободная лента",
            available_categories[1]: "Автошина",
            available_categories[2]: "Автошина",
            available_categories[3]: "Автокамера",
            available_categories[4]: "Диск",
        }
        for av_category in available_categories:
            if av_category in title:
                return categories_map[av_category]

        return "Разное"

    @classmethod
    def clear_and_set_title(cls, row_item: RowItem) -> None:
        """clear and set reared title"""
        row_item.title = row_item.title.replace(", , шт", "").strip()

    @classmethod
    def _prepare_title_chunks(cls, chunks: list[str]) -> list[str]:
        """get prepared title chunks"""
        # 6.00*17.5 -> 6.00x17.5
        for index, chunk in enumerate(chunks):
            if "*" in chunk and re.match(RE_PART_SIZE_PATTERN, chunk):
                chunks[index] = chunk.replace("*", "x")
        # 385/65  R22.5 -> 385/65R22.5
        if len(chunks) > 1 and re.match(RE_R_DIAMETER_PATTERN, chunks[1]):
            chunks[0] += chunks.pop(1)
        return chunks
