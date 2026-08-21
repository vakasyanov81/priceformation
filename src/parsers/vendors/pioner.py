"""
# из остатка вычитаем резерв, если полученный остаток меньше 2, то не учитываем
# попробовать выдергивать производителя из названия раздела и добавлять в наименование товара
# (после первого слова разделенного пробелом в наименовании)
# камеры по цене розницы
# шины триангл по цене розницы
# шины рокбастер 7% наценка на крупный опт.
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

PIONER_START_ROW = 12

pioner_params = ParserParams(
    supplier=ParseParamsSupplier(folder_name="pioner", name="Пионер", code="3"),
    start_row=PIONER_START_ROW,
    sheet_info="",
    columns={
        1: RowItem.title.name,
        2: RowItem.price_opt.name,
        4: RowItem.rest_count.name,
        5: RowItem.reserve_count.name,
    },
    stop_words=[],
    file_templates=["price*.xls", "price*.xlsx"],
    sheet_indexes=[],
    row_item_adaptor=RowItem,
)

mark_up_provider = data_provider.MarkupRulesProviderFromUserConfig(pioner_params.supplier.folder_name)

pioner_config = ParseConfiguration(
    BasePriceParseConfigurationParams(
        markup_rules_provider=mark_up_provider,
        black_list_provider=data_provider.BlackListProviderFromUserConfig(),
        stop_words_provider=data_provider.StopWordsProviderFromUserConfig(),
        vendor_list=data_provider.VendorListProviderFromUserConfig(),
        manufacturer_aliases=data_provider.ManufacturerAliasesProviderFromUserConfig(),
        parser_params=pioner_params,
    )
)

_MANUFACTURER_MAP = {"рокбастер": "RockBuster"}


def _display_manufacturer(manufacturer_name: str) -> str:
    """Map known manufacturer aliases for title."""
    return _MANUFACTURER_MAP.get(manufacturer_name, manufacturer_name)


class PionerParser(BaseParser):
    """
    parser for pioner vendor
    """

    current_category = None
    current_category_first_chunk = None

    def process_parsed_row(self, row_item: RowItem) -> None:
        self.skip_by_min_rest(row_item)
        self.add_price_markup(row_item)
        self.set_manufacturer_to_title(row_item)
        self.manufacturer_finder().process(row_item)

    def add_price_markup(self, row_item: RowItem) -> None:
        """
        Добавить наценку
        """

        price = row_item.price_opt or 0
        markup_percent = self.get_markup_percent(price) or 0
        price = (markup_percent + 1) * price
        row_item.price_markup = self.round_price(price)
        row_item.percent_markup = markup_percent * 100

    def skip_by_min_rest(self, row_item: RowItem) -> None:
        """skip by min rest"""
        self.set_current_category(row_item)
        if "прочие" in (self.current_category or "").lower():
            row_item.rest_count = 0
        return super().skip_by_min_rest(row_item)

    def set_current_category(self, row_item: RowItem) -> None:
        """set current category by title and type_production"""
        if self.is_category_row(row_item):
            self.current_category = (row_item.title or "").lower().strip()
        category = (self.current_category or "").split("/")[0]
        self.current_category_first_chunk = category.split(" ")[0]
        row_item.type_production = self.current_category_first_chunk
        self.correction_category(row_item)

    def set_manufacturer_to_title(self, row_item: RowItem) -> None:
        """set manufacturer name to title and brand for row item"""
        m_name = self.get_manufacturer_name()
        row_item.brand = m_name

        if not m_name or not row_item.price_opt:
            return

        display_name = _display_manufacturer(m_name)
        title = row_item.title
        if display_name.lower() in title.lower():
            return

        title_chunks = title.split(" ")
        title_chunks[0] = f"{title_chunks[0]} {display_name}"
        row_item.title = " ".join(title_chunks)

    def get_manufacturer_name(self) -> str | None:
        """determine manufacturer name by current category"""
        if not self.current_category:
            return None

        chunks = self.current_category.split(" ")

        if len(chunks) == 1:
            return None

        if chunks[0] != "автошины":
            return None

        return chunks[1]

    @classmethod
    def get_item_rest(cls, row_item: RowItem) -> int:
        """see base function"""
        rest = row_item.rest_count or 0
        reserve = row_item.reserve_count or 0
        return rest - reserve
