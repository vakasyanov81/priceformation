# -*- coding: utf-8 -*-
"""
logic for zapaska (rest) vendor
"""
__author__ = "Kasyanov V.A."
from typing import List, Optional, Tuple

from core.log_message import warn_msg
from parsers import data_provider
from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.base_parser_config import (
    BasePriceParseConfigurationParams,
    ParseConfiguration,
    ParseParamsSupplier,
    ParserParams,
)
from parsers.row_item.row_item import RowItem
from parsers.xls_reader import XlsReader

zapaska_rest_params = ParserParams(
    supplier=ParseParamsSupplier(
        folder_name="zapaska", name="Запаска (остатки)", code="2"
    ),
    start_row=9,
    sheet_info="",
    columns={
        0: RowItem.__CODE__,
        1: RowItem.__CODE_ART__,
        2: RowItem.__TITLE__,
        3: RowItem.__REST_COUNT__,
        4: RowItem.__PRICE_PURCHASE__,
    },
    stop_words=[],
    file_templates=["rest*.xls", "rest*.xlsx"],
    sheet_indexes=[],
    row_item_adaptor=RowItem,
)


mark_up_provider = data_provider.MarkupRulesProviderFromUserConfig(
    zapaska_rest_params.supplier.folder_name
)

zapaska_rest_config = BasePriceParseConfigurationParams(
    markup_rules_provider=mark_up_provider,
    black_list_provider=data_provider.BlackListProviderFromUserConfig(),
    stop_words_provider=data_provider.StopWordsProviderFromUserConfig(),
    vendor_list=data_provider.VendorListProviderFromUserConfig(),
    manufacturer_aliases=data_provider.ManufacturerAliasesProviderFromUserConfig(),
    parser_params=zapaska_rest_params,
)

zapaska_rest_config = ParseConfiguration(zapaska_rest_config)


class ZapaskaRestParser(BaseParser):
    """
    Parser rest and price opt for zapaska vendor
    """

    def __init__(
        self,
        parse_config,
        file_prices: list = None,
        xls_reader=XlsReader,
        price_mrp=None,
    ):
        """init"""
        self.price_sup_codes = {}
        self.rest_titles = {}
        self.price_mrp_result = []
        self.set_rest_and_price_opt(price_mrp)
        self.not_matched_position = []
        self._current_category = None
        super().__init__(parse_config, file_prices, xls_reader)

    def get_price_mrp_result(self) -> List[RowItem]:
        """price mrp result"""
        return self.price_mrp_result

    def process(self):
        """parse process"""
        count_processed = super().process()
        self.prepare_prices_mrp()

        for item in self.result:
            if self.is_category_row(item):
                current_category, _ = self._category_finder.find(item)
                self._current_category = current_category or self._current_category
            else:
                item.type_production = self._current_category

            self.make_price_markup(item)
            self.skip_by_min_rest(item)

        if self.not_matched_position:
            warn_msg(
                f"Всего несопоставленных позиций: {len(self.not_matched_position)}",
                need_print_log=True,
            )
            warn_msg(
                "Полный перечень несопоставленных позиций можно посмотреть в логах.",
                need_print_log=True,
            )
            for title in self.not_matched_position:
                warn_msg(title)

        return count_processed

    def set_rest_and_price_opt(self, rest_result):
        """get parse result for ZapaskaRest"""
        self.price_mrp_result = rest_result

    @classmethod
    def get_item_rest(cls, item: RowItem):
        """get rest count"""
        return item.rest_count

    def prepare_prices_mrp(self):
        """join result zapaska parser and zapaska rest parser via vendor position code"""
        for price_mrp in self.get_price_mrp_result():
            code = price_mrp.code or price_mrp.code_art

            self.price_sup_codes[code] = price_mrp.price_recommended

    @classmethod
    def _get_price_percent_markup(cls, price):
        """get price percent markup"""

        base_percent = 0.12
        base_percent_step = 0.02
        percent_map = {
            (0, 5000): base_percent + (base_percent_step * 5),
            (5000, 10000): base_percent + (base_percent_step * 4),
            (10000, 15000): base_percent + (base_percent_step * 2),
            (15000, 20000): base_percent + base_percent_step,
            (20000, 25000): base_percent,
        }

        default_percent_markup = base_percent

        for price_range, _percent_markup in percent_map.items():
            _min, _max = price_range
            if _min <= price < _max:
                return _percent_markup

        return default_percent_markup

    @classmethod
    def _make_price_markup(cls, price_recommended, price_opt):
        """set markup"""

        price, _ = cls._make_price_recommended_markup(price_recommended, price_opt)

        if not price:
            price = cls.get_markup(price_opt, cls._get_price_percent_markup(price_opt))

        return cls.make_absolute_markup(price, price_opt)

    @classmethod
    def make_absolute_markup(cls, price, price_opt, delta=150):
        """check price margin greater than delta"""
        if price - price_opt <= delta:
            return price_opt + delta
        return price

    @classmethod
    def _make_price_recommended_markup(
        cls, price_recommended, price_opt
    ) -> Tuple[Optional[float], Optional[float]]:
        """
        make markup for recommended price
        :param price_recommended:
        :param price_opt:
        :return: price_with_markup, percent_markup
        """
        if not price_recommended:
            return None, None

        percent = cls.calc_percent(price_recommended, price_opt)

        # Если наценка менее 8% запускаем алгоритм наценки
        if not cls._is_small_recommended_price(
            price_recommended, price_opt, percent=0.08
        ):
            return price_recommended, percent

        percent = cls._get_price_percent_markup(price_opt)

        return cls.get_markup(price_opt, percent), percent

    @classmethod
    def _is_small_recommended_price(cls, price_recommended, price_opt, percent) -> bool:
        """check margin for recommended price"""
        return (
            price_recommended
            and cls.calc_percent(price_recommended, price_opt) <= percent
        )

    def make_price_markup(self, item):
        """set markup
        цена закупа от 0 до 5000 прибавляем наценку 17%
        цена закупа от 5000 до 10000 прибавляем наценку 15%
        цена закупа от 10000 до 15000 прибавляем наценку 13%
        цена закупа от 15000 до 20000 прибавляем наценку 10%
        """
        code = item.code or item.code_art

        price_recommended = self.price_sup_codes.get(code) or self.find_rest_by_title(
            item.title
        )
        price_recommended = price_recommended or 0
        price_opt = item.price_opt

        if price_recommended:
            item.price_recommended = price_recommended

        if not price_opt:
            return

        if not price_recommended:
            self.not_matched_position.append(item.title)

        price_with_markup = self._make_price_markup(price_recommended, price_opt)
        item.price_markup = (
            self.round_price(price_with_markup) if price_with_markup else None
        )

    def find_rest_by_title(self, title):
        """find rest by title"""
        if not self.rest_titles:
            for item in self.get_price_mrp_result():
                if not item.title:
                    continue
                self.rest_titles[item.title.lower().strip()] = item.price_recommended
        return self.rest_titles.get(title.lower().strip())
