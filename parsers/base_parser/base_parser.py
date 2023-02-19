# -*- coding: utf-8 -*-
"""
base parser logic
"""
__author__ = "Kasyanov V.A."

import glob
import math
from functools import lru_cache
from typing import List, Type, TypeVar

from core.exceptions import CoreExceptionError
from parsers import data_provider
from parsers.base_item_actions.base_item_action import BaseItemAction
from parsers.base_item_actions.calc_percent_markup_item_action import SetPercentMarkupItemAction
from parsers.base_parser.category_finder import CategoryFinder
from parsers.base_parser.log_parser_process import LoggerParseProcess
from parsers.row_item.row_item import RowItem
from parsers.xls_reader import XlsReader

from ..data_provider import VendorParams
from .base_parser_config import BasePriceParseConfiguration
from .manufacturer_finder import ManufacturerFinder
from .parse_statistic import ParseResultStatistic

TBaseParser = TypeVar("TBaseParser", bound="BaseParser")


class BaseParser:
    """
    base parser logic
    """
    __SUPPLIER_FOLDER_NAME__ = "__"
    __START_ROW__ = 0

    __SUPPLIER_NAME__ = "Базовый поставщик"
    # Описание текущей вкладки
    __SHEET_INFO__ = ""
    __SUPPLIER_CODE__ = "*"

    __COLUMNS__ = {}
    __STOP_WORDS__ = []

    __FILE_TEMPLATES__ = ["price*.xls", "price*.xlsx"]

    __SHEET_INDEXES__ = []
    __ENABLE__ = False

    __ROW_ITEM_ADAPTOR__ = RowItem

    _item_actions: List[Type[BaseItemAction]] = []
    _item_actions_after_process: List[Type[BaseItemAction]] = [
        SetPercentMarkupItemAction
    ]

    def __init__(
            self,
            price_config: BasePriceParseConfiguration,
            file_prices: list = None,
            xls_reader=XlsReader
    ):
        """ init """
        self.result: List[RowItem] = []
        self._price_config = price_config
        self.type_production = None
        if not self.is_active:
            return
        self.logger = LoggerParseProcess(
            repr(self)
        )
        self.xls_reader = xls_reader
        self._category_finder = CategoryFinder()

        self.files = file_prices or get_file_prices(self)
        self.init_process()

    def price_config(self) -> BasePriceParseConfiguration:
        """ get price config """
        return self._price_config

    def markup_rules(self) -> data_provider.MarkupRules:
        """ get markup rules for price formation  """
        return self._price_config.get_markup_rules()

    @lru_cache()
    def get_black_list(self) -> List[str]:
        """ get black list price position """
        black_list = self._price_config.black_list()
        return self.prepare_black_list(black_list)

    def prepare_black_list(self, black_list: List[str]) -> List[str]:
        """ prepare black list """
        return [
            self.strip_words_in_title(black_title)
            for black_title in black_list
        ]

    @lru_cache()
    def get_stop_words(self) -> List[str]:
        """ get stop word list """
        return self._price_config.stop_words()

    def init_process(self):
        """ init process """
        if not self.is_active:
            self.logger.log_disable_status()
            return
        self.logger.log_start()
        self.process()
        self.after_process()
        self.logger.log_finish(ParseResultStatistic(self.result))

    def correction_category(self, item: RowItem):
        """ correction category """
        if not item.type_production:
            return
        category, bad_category = self._category_finder.find_in_str(item.type_production)
        if bad_category:
            item.type_production = category

    def process(self):
        """ parse process """
        result_statistic = 0
        self.logger.log_list_files(self.files)

        for _file in self.files:
            self.type_production = _file.split("_")[-1]
            res = self.to_row_items(
                self.raw_parse(_file)
            )
            result_statistic += len(res or [])
            self.result += res
        self.remove_without_price_purchase_and_check_valid_title()
        self.result = self.prepare(self.result)
        return result_statistic

    def after_process(self):
        """ make after process """
        self.remove_null_rest()
        self.do_items_actions_after_process()

    def get_markup_percent(self, price_value: float):
        """ get markup percent by price value """
        default_percent = self._price_config.get_default_markup_percents()

        if not price_value:
            return default_percent

        for price_rule in self._price_config.get_price_markup_map():
            if price_rule.min < price_value <= price_rule.max:
                return price_rule.percent

        return default_percent

    def prepare(self, items):
        """ prepare (need refactoring) """
        result = []

        for item in items:
            # сборка тайтла для мим-а
            self.set_prepared_title(item)

            # проверка на содержание стоп слов.
            if not self.is_valid_title(item.title):
                continue

            ManufacturerFinder(
                self._price_config.manufacturer_aliases()
            ).process(item)
            self.correction_category(item)

            item.supplier_name = self.__SUPPLIER_NAME__
            result.append(item)

        return result

    def do_items_actions_after_process(self):
        """ do after-process actions """
        for item in self.result:
            for item_action in self._item_actions_after_process:
                item_action(item).action()

    def __repr__(self) -> str:
        """ get supplier name and sheet info string """
        sup_name = f"{self.__class__.__name__}: {self.__SUPPLIER_NAME__}"
        if self.__SHEET_INFO__:
            sup_name += f" ({self.__SHEET_INFO__})"
        return sup_name

    def get_result(self) -> List[RowItem]:
        """ get parse result"""
        return self.result

    @property
    def is_active(self):
        """ supplier is active? """
        return bool(self.get_current_vendor_config().enabled)

    def remove_null_rest(self):
        """ remove from self.result items where rest count is Empty (0) """
        result = []
        for item in self.get_result():
            # rest_count may be ">40", its not convertible to float
            if not item.price_opt or not item.rest_count:
                continue
            result.append(item)

        self.result = result

    def remove_without_price_purchase_and_check_valid_title(self):
        """ .... """
        result = []
        for item in self.get_result():
            if item.rest_count and not item.price_opt:
                continue
            if item.title and not self.is_valid_title(item.title):
                continue
            result.append(item)

        self.result = result

    @classmethod
    def to_row_items(cls, result: List[dict]) -> List[RowItem]:
        """ instance List[RowItem] """
        return [
            cls.__ROW_ITEM_ADAPTOR__(raw_item)
            for raw_item in result
        ]

    @classmethod
    def to_raw_result(cls, result: List[RowItem]) -> List[dict]:
        """ instance List[dict] """
        return [
            item.to_dict()
            for item in result
        ]

    def raw_parse(self, _file: str) -> List[dict]:
        """ get raw-data after parse via reader """
        reader = self.get_xls_reader(_file)
        return reader.parse(self.__SHEET_INDEXES__)

    def get_xls_reader(self, _file):
        """ get xls reader """
        return self.xls_reader.get_instance(
            _file,
            {
                "start_row": (self.__START_ROW__ - 1),
                "columns": self.__COLUMNS__
            }
        )

    @classmethod
    def get_prepared_title(cls, item):
        """ get title with modification (use in child-parser if need) """
        return item.title

    @classmethod
    def set_prepared_title(cls, item: RowItem) -> bool:
        """
        set prepared title
        :return title is prepared
        """
        prepared_title = cls.get_prepared_title(item)
        title_is_prepared = item.title == prepared_title
        item.title = prepared_title or item.title
        return title_is_prepared

    def is_valid_title(self, title: str):
        """ validation for title """
        return title and not self.has_stop_word(title) and not self.check_title_in_black_list(title)

    def has_stop_word(self, title) -> bool:
        """ checking that title contains a stop word """
        for s_word in self.get_stop_words():
            if s_word.lower() in title.lower():
                return True
        return False

    def check_title_in_black_list(self, title) -> bool:
        """ checking that title in black list """
        return title in self.get_black_list()

    @classmethod
    def get_min_rest_count(cls):
        """ min rest count value for skip action """
        return 4

    @classmethod
    def get_item_rest(cls, item: RowItem):
        """ get rest count """
        return item.rest_count

    def skip_by_min_rest(self, item: RowItem):
        """ skip row item where rest count less than.. """
        if self.get_item_rest(item) < self.get_min_rest_count():
            item.rest_count = 0

    @classmethod
    def round_price(cls, price_value) -> float:
        """
        make round price_value
        125.45 -> 130.0
        """
        return math.ceil(price_value / 10) * 10

    @classmethod
    def is_category_row(cls, item):
        """ determine current category by specific row item """
        if item.title and not item.price_opt:
            return True
        return False

    @classmethod
    @lru_cache()
    def calc_percent(cls, price_sale, price_purchase):
        """ calc margin percent """
        return (price_sale - price_purchase) / price_purchase

    @lru_cache()
    def recommended_percent_markup(self, item) -> float:
        """ percent markup betwen purchase price and recommended price"""
        price_recommended = item.price_recommended or 0
        price_opt = item.price_opt or 0
        return self.calc_percent(price_recommended, price_opt) if price_recommended else 0

    def is_small_recommended_percent(self, item) -> bool:
        """ percent markup is small to much? """
        return self.recommended_percent_markup(item) < self.markup_rules().min_recommended_percent_markup

    def is_big_recommended_percent(self, item) -> bool:
        """ percent markup is big? """
        if not self.markup_rules().max_recommended_percent_markup:
            return False
        return self.recommended_percent_markup(item) > self.markup_rules().max_recommended_percent_markup

    def is_small_absolute_markup(self, selling_price, purchase_price) -> bool:
        """ absolute markup from purchase price and selling price is small to much? """
        return selling_price - purchase_price < self.markup_rules().absolute_markup_rules.min_absolute_markup

    def get_price_with_absolute_rule_markup(self, price_opt) -> float:
        """ get price as absolute markup from purchase price """
        return price_opt * self.markup_rules().absolute_markup_rules.markup_percent

    def add_price_markup(self, item):
        """ add markup to row item """

        price = item.price_recommended or 0
        price_opt = item.price_opt or 0

        if self.is_small_recommended_percent(item):
            price = self.get_markup(price_opt, self.get_markup_percent(price_opt))

        if self.is_big_recommended_percent(item):
            price = self.get_markup(price_opt, self.markup_rules().max_recommended_percent_markup)

        if self.is_small_absolute_markup(price, price_opt):
            price = self.get_price_with_absolute_rule_markup(price_opt)

        item.price_markup = self.round_price(price)

    @classmethod
    @lru_cache()
    def get_markup(cls, price, percent):
        """ get price with markup"""
        return price * (1 + percent)

    def get_current_vendor_config(self) -> data_provider.VendorParams:
        """ get config for current vendor """
        return self._price_config.all_vendor_config().get(self.__SUPPLIER_FOLDER_NAME__) or VendorParams(enabled=0)

    @classmethod
    def prepare_title(cls, title: str):
        """ make correct title format """
        chunks = cls.strip_chunks_title(title.split())
        chunks = cls._prepare_title_chunks(chunks)
        return " ".join(chunks)

    @classmethod
    def _prepare_title_chunks(cls, chunks: List[str]) -> List[str]:
        """ get prepared title chunks """
        return chunks

    @classmethod
    def strip_chunks_title(cls, chunks: list):
        """
        [" 385/65  ", " R22.5", ...] -> ["385/65", "R22.5", ...]
        :param chunks:
        :return:
        """
        return [
            chunk.strip()
            for chunk in chunks
            if chunk.strip()
        ]

    @classmethod
    def strip_words_in_title(cls, title: str):
        """
        " 385/65   R22.5..." -> "385/65 R22.5..."
        :param title:
        :return:
        """
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


class SupplierNotHavePricesError(CoreExceptionError):
    """ exception for case when not prices """


def get_file_prices(parser: TBaseParser):
    """ get supplier file-prices """
    _list_files = []
    for f_tmp in parser.__FILE_TEMPLATES__:
        _list_files += glob.glob(f"file_prices/{parser.__SUPPLIER_FOLDER_NAME__}/{f_tmp}")

    if not _list_files:
        raise SupplierNotHavePricesError(f"Прайсов у поставщика ({parser.__SUPPLIER_NAME__}) не обнаружено!")
    return _list_files
