# -*- coding: utf-8 -*-
"""
# из остатка вычитаем резерв, если полученный остаток меньше 2, то не учитываем
# попробовать выдергивать производителя из названия раздела и добавлять в наименование товара
# (после первого слова разделенного пробелом в наименовании)
# камеры по цене розницы
# шины триангл по цене розницы
# шины рокбастер 7% наценка на крупный опт.
"""
__author__ = "Kasyanov V.A."

from parsers import data_provider
from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.base_parser_config import (
    BasePriceParseConfigurationParams,
    ParseConfiguration,
    ParseParamsSupplier,
    ParserParams,
)
from parsers.base_parser.manufacturer_finder import ManufacturerFinder
from parsers.row_item.row_item import RowItem

pioner_params = ParserParams(
    supplier=ParseParamsSupplier(folder_name="pioner", name="Пионер", code="3"),
    start_row=12,
    sheet_info="",
    columns={
        1: RowItem.__TITLE__,
        2: RowItem.__PRICE_PURCHASE__,
        4: RowItem.__REST_COUNT__,
        5: RowItem.__RESERVE_COUNT__,
    },
    stop_words=[],
    file_templates=["price*.xls", "price*.xlsx"],
    sheet_indexes=[],
    row_item_adaptor=RowItem,
)


mark_up_provider = data_provider.MarkupRulesProviderFromUserConfig(
    pioner_params.supplier.folder_name
)

pioner_config = BasePriceParseConfigurationParams(
    markup_rules_provider=mark_up_provider,
    black_list_provider=data_provider.BlackListProviderFromUserConfig(),
    stop_words_provider=data_provider.StopWordsProviderFromUserConfig(),
    vendor_list=data_provider.VendorListProviderFromUserConfig(),
    manufacturer_aliases=data_provider.ManufacturerAliasesProviderFromUserConfig(),
    parser_params=pioner_params,
)

pioner_config = ParseConfiguration(pioner_config)


class PionerParser(BaseParser):
    """
    parser for pioner vendor
    """

    current_category = None
    current_category_first_chunk = None

    def process(self):
        res = super().process()
        for item in self.result:
            self.skip_by_min_rest(item)
            self._set_current_category(item)
            self.set_current_category(item)
            self.add_price_markup(item)
            self.set_manufacturer_to_title(item)
            self.set_brand(item)
            ManufacturerFinder(self.parse_config().manufacturer_aliases()).process(item)

        return res

    def _set_current_category(self, item):
        """set current category by title"""
        if self.is_category_row(item):
            self.current_category = (item.title or "").lower().strip()
        self.current_category_first_chunk = (
            (self.current_category or "").split("/")[0]
        ).split(" ")[0]

    def set_manufacturer_to_title(self, item):
        """set manufacturer name to title for row item"""
        m_name = self.get_manufacturer_name()

        def make_m_name(_m_name):
            _m_map = {"рокбастер": "RockBuster"}

            return _m_map.get(m_name) or m_name

        if not m_name or not item.price_opt:
            return

        title = item.title

        title_chunks = title.split(" ")

        title_chunks[0] = f"{title_chunks[0]} {make_m_name(m_name)}"

        item.title = " ".join(title_chunks)

    def set_brand(self, item):
        """set brand name"""
        m_name = self.get_manufacturer_name()
        item.brand = m_name

    def set_current_category(self, item: RowItem):
        """set current category"""
        item.type_production = self.current_category_first_chunk
        self.correction_category(item)

    def get_manufacturer_name(self):
        """determine manufacturer name by current category"""
        if not self.current_category:
            return None

        chunks = self.current_category.split(" ")

        if len(chunks) == 1:
            return None

        if chunks[0] != "автошины":
            return None

        cur_category_name = chunks[1]

        return cur_category_name

    @classmethod
    def get_item_rest(cls, item):
        """see base function"""
        rest = item.rest_count or 0
        reserve = item.reserve_count or 0
        return rest - reserve

    def add_price_markup(self, item):
        """
        Добавить наценку
        """

        if not item.price_opt:
            return
        item.price_markup = self.round_price(item.price_opt * 1.04)
