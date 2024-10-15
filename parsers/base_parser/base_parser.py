# -*- coding: utf-8 -*-
"""
base parser logic
"""
__author__ = "Kasyanov V.A."

import glob
from functools import lru_cache
from typing import List, Type, TypeVar

import math

from core.exceptions import SupplierNotHavePricesError
from parsers import data_provider
from parsers.base_item_actions.base_item_action import BaseItemAction
from parsers.base_item_actions.calc_percent_markup_item_action import (
    SetPercentMarkupItemAction,
)
from parsers.base_parser.category_finder import CategoryFinder
from parsers.base_parser.log_parser_process import LoggerParseProcess
from parsers.row_item.row_item import RowItem
from parsers.xls_reader import XlsReader
from .base_parser_config import ParseConfiguration, ParserParams
from .manufacturer_finder import ManufacturerFinder
from .parse_statistic import ParseResultStatistic
from ..data_provider import VendorParams

BaseParserT = TypeVar("BaseParserT", bound="BaseParser")


class BaseParser:
    """Base parser logic"""

    _item_actions: List[Type[BaseItemAction]] = []
    _item_actions_after_process: List[Type[BaseItemAction]] = [
        SetPercentMarkupItemAction
    ]

    _params = None
    _category_finder = None
    files = None

    def __init__(
        self,
        parse_config: ParseConfiguration = None,
        file_prices: list = None,
        xls_reader=XlsReader,
    ):
        self.result: List[RowItem] = []
        self._parse_config = parse_config
        self.type_production = None
        self.xls_reader = xls_reader
        self.files = file_prices
        self.logger = LoggerParseProcess(repr(self))

    def parse_config(self) -> ParseConfiguration:
        """get parse configuration"""
        return self._parse_config

    def markup_rules(self) -> data_provider.MarkupRules:
        """get markup rules"""
        return self._parse_config.get_markup_rules()

    @lru_cache()
    def get_black_list(self) -> List[str]:
        """get black list"""
        black_list = self._parse_config.black_list()
        return self.prepare_black_list(black_list)

    def prepare_black_list(self, black_list: List[str]) -> List[str]:
        """prepare black list"""
        return [self.strip_words_in_title(black_title) for black_title in black_list]

    @lru_cache()
    def get_stop_words(self) -> List[str]:
        """get stop word list"""
        return self._parse_config.stop_words()

    def set_parse_config(self, parse_config: ParseConfiguration):
        """set parse configuration"""
        self._parse_config = parse_config

    def parse(self):
        """parse price"""
        if not self.is_active:
            self.logger.log_disable_status()
            return []
        self._category_finder = CategoryFinder()
        self.files = self.files or get_file_prices(self)
        self.logger.log_start()
        self.process()
        self.after_process()
        self.logger.log_finish(ParseResultStatistic(self.result))
        return self.result

    def correction_category(self, item: RowItem):
        """check and fix wrong category title"""
        if not item.type_production:
            return
        category, bad_category = self._category_finder.find_in_str(item.type_production)
        if bad_category:
            item.type_production = category

    def process(self):
        """main parse process"""
        result_statistic = 0
        self.logger.log_list_files(self.files)

        for _file in self.files:
            self.type_production = _file.split("_")[-1]
            res = self.to_row_items(self.raw_parse(_file))
            result_statistic += len(res or [])
            self.result += res
        self.remove_without_price_purchase_and_check_valid_title()
        self.result = self.process_price_items(self.result)
        return result_statistic

    def after_process(self):
        """after price parse process"""
        self.remove_null_rest()
        self.make_actions_after_process()

    def make_actions_after_process(self):
        """apply actions with price items"""
        for item in self.result:
            for item_action in self._item_actions_after_process:
                item_action(item).action()

    def get_markup_percent(self, price_value: float):
        """get markup percent"""
        default_percent = self._parse_config.get_default_markup_percents()

        if not price_value:
            return default_percent

        for price_rule in self._parse_config.get_price_markup_map():
            if price_rule.min < price_value <= price_rule.max:
                return price_rule.percent

        return default_percent

    def parser_params(self) -> ParserParams:
        """get parse params"""
        return self.parse_config().parse_config.parser_params

    def process_price_items(self, items):
        """process price items"""
        result = []

        for item in items:
            self.set_prepared_title(item)

            # проверка на содержание стоп слов.
            if not self.is_valid_title(item.title):
                continue

            ManufacturerFinder(self._parse_config.manufacturer_aliases()).process(item)
            self.correction_category(item)

            item.supplier_name = self.parser_params().supplier.name
            result.append(item)

        return result

    def __repr__(self) -> str:
        sup_name = f"{self.__class__.__name__}: {self.parser_params().supplier.name}"
        if self.parser_params().sheet_info:
            sup_name += f" ({self.parser_params().sheet_info})"
        return sup_name

    def get_result(self) -> List[RowItem]:
        """get result"""
        return self.result

    @property
    def is_active(self):
        """vendor is active?"""
        return bool(self.get_current_vendor_config().enabled)

    def remove_null_rest(self):
        """remove items with null rest"""
        result = []
        for item in self.get_result():
            # rest_count may be ">40", its not convertible to float
            if not item.price_opt or not item.rest_count:
                continue
            result.append(item)

        self.result = result

    def remove_without_price_purchase_and_check_valid_title(self):
        """remove invalid items"""
        result = []
        for item in self.get_result():
            if item.rest_count and not item.price_opt:
                continue
            if item.title and not self.is_valid_title(item.title):
                continue
            result.append(item)

        self.result = result

    def to_row_items(self, result: List[dict]) -> List[RowItem]:
        """get list row"""
        return [self.parser_params().row_item_adaptor(row_item) for row_item in result]

    @classmethod
    def to_raw_result(cls, result: List[RowItem]) -> List[dict]:
        """get dictable list"""
        return [item.to_dict() for item in result]

    def raw_parse(self, _file: str) -> List[dict]:
        """run low level parse"""
        reader = self.get_xls_reader(_file)
        return reader.parse(self.parser_params().sheet_indexes)

    def get_xls_reader(self, _file):
        """get xls / xlsx reader instance"""
        return self.xls_reader.get_instance(
            _file,
            {
                "start_row": (self.parser_params().start_row - 1),
                "columns": self.parser_params().columns,
            },
        )

    @classmethod
    def get_prepared_title(cls, item):
        """get prepared title"""
        return item.title

    @classmethod
    def set_prepared_title(cls, item: RowItem) -> bool:
        """set prepared title in item"""
        prepared_title = cls.get_prepared_title(item)
        title_is_prepared = item.title == prepared_title
        item.title = prepared_title or item.title
        return title_is_prepared

    def is_valid_title(self, title: str):
        """title is valid?"""
        return (
            title
            and not self.has_stop_word(title)
            and not self.check_title_in_black_list(title)
        )

    def has_stop_word(self, title) -> bool:
        """check title contains stop word"""
        for s_word in self.get_stop_words():
            if s_word.lower() in title.lower():
                return True
        return False

    def check_title_in_black_list(self, title) -> bool:
        """check title in black list"""
        return title in self.get_black_list()

    @classmethod
    def get_min_rest_count(cls):
        """get min rest count"""
        return 4

    @classmethod
    def get_item_rest(cls, item: RowItem):
        return item.rest_count

    def skip_by_min_rest(self, item: RowItem):
        """set rest_count = 0 for item where rest_count less than min"""
        if self.get_item_rest(item) < self.get_min_rest_count():
            item.rest_count = 0

    @classmethod
    def round_price(cls, price_value) -> float:
        """round money"""
        return math.ceil(price_value / 10) * 10

    @classmethod
    def is_category_row(cls, item):
        """item is folder?"""
        if item.title and not item.price_opt:
            return True
        return False

    @classmethod
    @lru_cache()
    def calc_percent(cls, price_sale, price_purchase):
        """calculate percent"""
        return (price_sale - price_purchase) / price_purchase

    @lru_cache()
    def recommended_percent_markup(self, item) -> float:
        """calculate recommended percent markup"""
        price_recommended = item.price_recommended or 0
        price_opt = item.price_opt or 0
        return (
            self.calc_percent(price_recommended, price_opt) if price_recommended else 0
        )

    def is_small_recommended_percent(self, item) -> bool:
        """is small recommended percent?"""
        return (
            self.recommended_percent_markup(item)
            < self.markup_rules().min_recommended_percent_markup
        )

    def is_big_recommended_percent(self, item) -> bool:
        """big percent?"""
        if not self.markup_rules().max_recommended_percent_markup:
            return False
        return (
            self.recommended_percent_markup(item)
            > self.markup_rules().max_recommended_percent_markup
        )

    def is_small_absolute_markup(self, selling_price, purchase_price) -> bool:
        """is small abs markup?"""
        return (
            selling_price - purchase_price
            < self.markup_rules().absolute_markup_rules.min_absolute_markup
        )

    def get_price_with_absolute_rule_markup(self, price_opt) -> float:
        return price_opt * self.markup_rules().absolute_markup_rules.markup_percent

    def add_price_markup(self, item):
        price = item.price_recommended or 0
        price_opt = item.price_opt or 0

        if self.is_small_recommended_percent(item):
            price = self.get_markup(price_opt, self.get_markup_percent(price_opt))

        if self.is_big_recommended_percent(item):
            price = self.get_markup(
                price_opt, self.markup_rules().max_recommended_percent_markup
            )

        if self.is_small_absolute_markup(price, price_opt):
            price = self.get_price_with_absolute_rule_markup(price_opt)

        item.price_markup = self.round_price(price)

    @classmethod
    @lru_cache()
    def get_markup(cls, price, percent):
        return price * (1 + percent)

    def get_current_vendor_config(self) -> data_provider.VendorParams:
        return self._parse_config.all_vendor_config().get(
            self.parser_params().supplier.folder_name
        ) or VendorParams(enabled=0)

    @classmethod
    def prepare_title(cls, title: str):
        chunks = cls.strip_chunks_title(title.split())
        chunks = cls._prepare_title_chunks(chunks)
        return " ".join(chunks)

    @classmethod
    def _prepare_title_chunks(cls, chunks: List[str]) -> List[str]:
        return chunks

    @classmethod
    def strip_chunks_title(cls, chunks: list):
        # [" 385/65  ", " R22.5", ...] -> ["385/65", "R22.5", ...]
        return [chunk.strip() for chunk in chunks if chunk.strip()]

    @classmethod
    def strip_words_in_title(cls, title: str):
        # " 385/65   R22.5..." -> "385/65 R22.5..."
        _title = (title or "").strip()
        if not _title:
            return title

        chunks = title.split()
        new_chunks = []

        for chunk in chunks:
            chunk = chunk.strip()
            if not chunk:
                continue
            new_chunks.append(chunk)
        return " ".join(new_chunks)


def get_file_prices(parser: BaseParserT):
    _list_files = []
    for f_tmp in parser.parser_params().file_templates:
        _list_files += glob.glob(
            f"file_prices/{parser.parser_params().supplier.folder_name}/{f_tmp}"
        )

    if not _list_files:
        raise SupplierNotHavePricesError(
            f"Прайсов у поставщика ({parser.parser_params().supplier.name}) не обнаружено!"
        )
    return _list_files
