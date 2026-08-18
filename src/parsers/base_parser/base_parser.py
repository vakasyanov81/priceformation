"""
base parser logic
"""

import math
from functools import lru_cache
from pathlib import Path
from typing import Any, List, Optional, Protocol, Type, TypeVar

from core.exceptions import SupplierNotHavePricesError
from core.parse_paths import get_parse_paths
from parsers import data_provider
from parsers.base_item_actions.base_item_action import BaseItemAction
from parsers.base_item_actions.calc_percent_markup_item_action import (
    SetPercentMarkupItemAction,
)
from parsers.base_parser.category_finder import CategoryFinder
from parsers.base_parser.log_parser_process import LoggerParseProcess
from parsers.row_item.row_item import RowItem
from parsers.xls_reader import IXlsReader, XlsReader

from ..data_provider import VendorParams
from . import price_markup
from .base_parser_config import ParseConfiguration, ParserParams
from .base_parser_row import _keep_row_item, _try_prepare_row
from .parse_statistic import ParseResultStatistic

TBaseParser = TypeVar("TBaseParser", bound="BaseParser")


class XlsReaderFactory(Protocol):
    """Класс-ридер с фабричным get_instance (XlsReader / FakeXlsReader)."""

    @classmethod
    def get_instance(cls, file_path: str, *args: Any, **kwargs: Any) -> IXlsReader: ...


class Parser(Protocol):
    """parser protocol"""

    @classmethod
    def supplier_folder_name(cls) -> str:
        """supplier folder name"""

    def get_parsed_items(self) -> List[RowItem]:
        """get parsed items"""

    def parse(self) -> List[RowItem]:
        """parse price files"""


class BaseParser:
    _item_actions: List[Type[BaseItemAction]] = []
    _item_actions_after_process: List[Type[BaseItemAction]] = [SetPercentMarkupItemAction]

    def __init__(
        self,
        parse_config: Optional[ParseConfiguration] = None,
        file_prices: list[str] | None = None,
        xls_reader: type[XlsReaderFactory] = XlsReader,
    ) -> None:
        self.parsed_items: List[RowItem] = []
        self._parse_config: ParseConfiguration | None = parse_config
        self.type_production: str | None = None
        self.xls_reader = xls_reader
        self.files: list[str] | None = file_prices
        self.logger = LoggerParseProcess(repr(self))
        self._black_list: List[str] | None = None
        self._stop_words: List[str] | None = None
        self._category_finder: CategoryFinder | None = None
        self.unknown_category_skips: list[str] = []

    def parse_config(self) -> ParseConfiguration:
        if self._parse_config is None:
            raise RuntimeError("parse_config is not set")
        return self._parse_config

    def markup_rules(self) -> data_provider.MarkupRules:
        return self.parse_config().get_markup_rules()

    def get_black_list(self) -> List[str]:
        if self._black_list is None:
            self._black_list = self.prepare_black_list(self.parse_config().black_list())
        return self._black_list

    def prepare_black_list(self, black_list: List[str]) -> List[str]:
        return [self.strip_words_in_title(black_title) for black_title in black_list]

    def get_stop_words(self) -> List[str]:
        if self._stop_words is None:
            self._stop_words = self.parse_config().stop_words()
        return self._stop_words

    def set_parse_config(self, parse_config: ParseConfiguration) -> None:
        self._parse_config = parse_config
        self._black_list = None
        self._stop_words = None

    def parse(self) -> List[RowItem]:
        if not self.is_active:
            self.logger.log_disable_status()
            return []
        self._category_finder = CategoryFinder()
        self.files = self.files or get_file_prices(self)
        self.logger.log_start()
        self.process()
        self.after_process()
        self.logger.log_finish(ParseResultStatistic(self.parsed_items))
        return self.parsed_items

    def correction_category(self, row_item: RowItem) -> None:
        if not row_item.type_production or self._category_finder is None:
            return
        category, bad_category = self._category_finder.find_in_str(row_item.type_production)
        if bad_category:
            row_item.type_production = category

    def process(self) -> int:
        result_statistic = 0
        files = self.files or []
        self.logger.log_list_files(files)

        for price_file in files:
            self.type_production = price_file.split("_")[-1]
            res = self.to_row_items(self.raw_parse(price_file))
            result_statistic += len(res or [])
            self.parsed_items += res
        self.remove_wo_price_purchase_and_check_title()
        self.parsed_items = self.prepare(self.parsed_items)
        return result_statistic

    def after_process(self) -> None:
        self.remove_null_rest()
        self.do_items_actions_after_process()

    def get_markup_percent(self, price_value: float) -> float:
        parse_config = self.parse_config()
        markup_map = parse_config.get_price_markup_map()
        default_percent = min({price_rule.percent_markup for price_rule in markup_map} or (0,))

        if not price_value:
            return default_percent

        for price_rule in markup_map:
            if price_rule.min <= price_value <= price_rule.max:
                return price_rule.percent_markup

        return default_percent

    def parser_params(self) -> ParserParams:
        return self.parse_config().parse_config.parser_params

    def prepare(self, row_items: list[RowItem]) -> list[RowItem]:
        parsed_items = []
        start_row = self.parse_config().parse_config.parser_params.start_row
        for row_id, row_item in enumerate(row_items, start=start_row):
            prepared = _try_prepare_row(self, row_id, row_item)
            if prepared is not None:
                parsed_items.append(prepared)
        return parsed_items

    def do_items_actions_after_process(self) -> None:
        for row_item in self.parsed_items:
            for item_action in self._item_actions_after_process:
                item_action(row_item).action()

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        supplier_name = self.parser_params().supplier.name
        sup_name = f"{class_name}: {supplier_name}"
        sheet_info = self.parser_params().sheet_info
        if sheet_info:
            sup_name = f"{sup_name} ({sheet_info})"
        return sup_name

    def get_parsed_items(self) -> List[RowItem]:
        return self.parsed_items

    @property
    def is_active(self) -> bool:
        return bool(self.get_current_vendor_config().enabled)

    def remove_null_rest(self) -> None:
        filtered_items = []
        for row_item in self.get_parsed_items():
            # rest_count may be ">40", its not convertible to float
            if not row_item.price_opt or not row_item.rest_count:
                continue
            filtered_items.append(row_item)

        self.parsed_items = filtered_items

    @classmethod
    def replace_season(cls, row_item: RowItem) -> str | None:
        if not row_item.season:
            return None
        replaced_seasons = {"зима": "Зимняя", "лето": "Летняя"}
        return replaced_seasons.get(row_item.season.lower()) or row_item.season

    def remove_wo_price_purchase_and_check_title(self) -> None:
        """...."""
        self.parsed_items = [row_item for row_item in self.get_parsed_items() if _keep_row_item(self, row_item)]

    def to_row_items(self, raw_rows: List[dict[str, Any]]) -> List[RowItem]:
        return [self.parser_params().row_item_adaptor(row_item) for row_item in raw_rows]

    def raw_parse(self, full_file_xls_path: str) -> List[dict[str, Any]]:
        reader = self.get_xls_reader(full_file_xls_path)
        return reader.parse(self.parser_params().sheet_indexes)

    def get_xls_reader(self, full_file_xls_path: str) -> IXlsReader:
        return self.xls_reader.get_instance(
            full_file_xls_path,
            {
                "start_row": self.parser_params().start_row - 1,
                "columns": self.parser_params().columns,
            },
        )

    @classmethod
    def get_prepared_title(cls, row_item: RowItem) -> str:
        return row_item.title

    def set_prepared_title(self, row_item: RowItem) -> bool:
        prepared_title = self.get_prepared_title(row_item)
        title_is_prepared = row_item.title == prepared_title
        row_item.title = prepared_title or row_item.title
        return title_is_prepared

    def is_valid_title(self, title: str) -> bool:
        has_content = bool(title)
        no_stop = not self.has_stop_word(title)
        not_blacklisted = not self.check_title_in_black_list(title)
        return has_content and no_stop and not_blacklisted

    def has_stop_word(self, title: str) -> bool:
        for s_word in self.get_stop_words():
            if s_word.lower() in title.lower():
                return True
        return False

    def check_title_in_black_list(self, title: str) -> bool:
        return title in self.get_black_list()

    @classmethod
    def get_min_rest_count(cls) -> int:
        return 4

    @classmethod
    def get_item_rest(cls, row_item: RowItem) -> Any:
        return row_item.rest_count

    def skip_by_min_rest(self, row_item: RowItem) -> None:
        if self.get_item_rest(row_item) < self.get_min_rest_count():
            row_item.rest_count = 0

    @classmethod
    def round_price(cls, price_value: float) -> float:
        """rounding to cents"""
        return math.ceil(price_value / 10) * 10

    @classmethod
    def is_category_row(cls, row_item: RowItem) -> bool:
        """is category row?"""
        if row_item.title and not row_item.price_opt:
            return True
        return False

    @classmethod
    @lru_cache()
    def calc_percent(cls, price_sale: float, price_purchase: float) -> float:
        """calc margin percentage"""
        return price_markup.calc_percent(price_sale, price_purchase)

    def recommended_percent_markup(self, row_item: RowItem) -> float:
        """calculate recommended percent markup"""
        price_recommended = row_item.price_recommended or 0
        price_opt = row_item.price_opt or 0
        return self.calc_percent(price_recommended, price_opt) if price_recommended else 0

    def is_small_recommended_percent(self, row_item: RowItem) -> bool:
        """absolute percent markup is small?"""
        return self.recommended_percent_markup(row_item) < self.markup_rules().min_recommended_percent_markup

    def is_big_recommended_percent(self, row_item: RowItem) -> bool:
        """recommended supplier markup percent is big?"""
        if not self.markup_rules().max_recommended_percent_markup:
            return False
        return self.recommended_percent_markup(row_item) > self.markup_rules().max_recommended_percent_markup

    def is_small_absolute_markup(self, selling_price: float, purchase_price: float) -> bool:
        """absolute markup is small?"""
        return selling_price - purchase_price < self.markup_rules().absolute_markup_rules.min_absolute_markup

    def get_price_with_absolute_rule_markup(self, price_opt: float) -> float:
        """absolute markup value"""
        return price_opt * self.markup_rules().absolute_markup_rules.markup_percent

    def add_price_markup(self, row_item: RowItem) -> None:
        """calculate and fill price_markup field"""
        price = row_item.price_recommended or 0
        price_opt = row_item.price_opt or 0

        if self.is_small_recommended_percent(row_item) and not row_item.price_recommended:
            price = self.get_markup(price_opt, self.get_markup_percent(price_opt))

        if self.is_big_recommended_percent(row_item) and not row_item.price_recommended:
            price = self.get_markup(price_opt, self.markup_rules().max_recommended_percent_markup)

        if self.is_small_absolute_markup(price, price_opt):
            price = self.get_price_with_absolute_rule_markup(price_opt)

        row_item.price_markup = self.round_price(price)

    @classmethod
    @lru_cache()
    def get_markup(cls, price: float, percent: float) -> float:
        """get price with absolute markup"""
        return price_markup.get_markup(price, percent)

    def get_current_vendor_config(self) -> data_provider.VendorParams:
        """get vendor configuration"""
        folder_name = self.parser_params().supplier.folder_name
        vendor = self.parse_config().all_vendor_config().get(folder_name)
        return vendor or VendorParams(enabled=0)

    @classmethod
    def prepare_title(cls, title: str) -> str:
        """prepare title"""
        chunks = cls.strip_chunks_title(title.split())
        chunks = cls._prepare_title_chunks(chunks)
        return " ".join(chunks)

    @classmethod
    def _prepare_title_chunks(cls, chunks: List[str]) -> List[str]:
        return chunks

    @classmethod
    def strip_chunks_title(cls, chunks: list[str]) -> list[str]:
        """# [" 385/65  ", " R22.5", ...] -> ["385/65", "R22.5", ...]"""
        return [chunk.strip() for chunk in chunks if chunk.strip()]

    @classmethod
    def strip_words_in_title(cls, title: str) -> str:
        """ " 385/65   R22.5..." -> "385/65 R22.5..." """
        stripped_title = (title or "").strip()
        if not stripped_title:
            return title

        chunks = title.split()
        new_chunks = []

        for chunk in chunks:
            chunk = chunk.strip()
            if not chunk:
                continue
            new_chunks.append(chunk)
        return " ".join(new_chunks)

    @classmethod
    def get_spike_title(cls, row_item: RowItem) -> str:
        """Наличие шипа"""
        if not row_item.spike:
            return ""
        if row_item.spike.strip().lower() in ["ш.", "да"]:
            return "Да"
        return ""


def _glob_price_files(supplier_folder: Path, templates: list[str]) -> list[str]:
    """Собрать пути прайсов по glob-шаблонам."""
    list_files: list[str] = []
    for f_tmp in templates:
        list_files.extend(str(path) for path in supplier_folder.glob(f_tmp))
    return list_files


def get_file_prices(parser: TBaseParser) -> list[str]:
    """get file prices"""
    prices_root = Path(get_parse_paths().file_prices_folder)
    supplier_folder = prices_root / parser.parser_params().supplier.folder_name
    list_files = _glob_price_files(supplier_folder, parser.parser_params().file_templates)

    if not list_files:
        supplier_name = parser.parser_params().supplier.name
        raise SupplierNotHavePricesError(f"Прайсов у поставщика ({supplier_name}) не обнаружено!")
    return list_files
