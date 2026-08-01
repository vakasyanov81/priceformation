"""
logic for zapaska (rest) vendor
"""

import json
from pathlib import Path
from typing import List, Optional, Tuple

from cfg.main import MainConfig
from core.file_reader import read_file
from parsers import data_provider
from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.base_parser_config import (
    BasePriceParseConfigurationParams,
    ParseConfiguration,
    ParseParamsSupplier,
    ParserParams,
)
from parsers.row_item.row_item import RowItem

_BASE_PERCENT = 0.12

column_mapping = {
    "cae": RowItem.code_art.name,
    "rest": RowItem.rest_count.name,
    "price": RowItem.price_opt.name,
    "retail": RowItem.price_recommended.name,
    "diam_center": RowItem.central_diameter.name,
    "holes": RowItem.slot_count.name,
    "diam_holes": RowItem.slot_diameter.name,
    "ET": RowItem.eet.name,
    "brand": RowItem.manufacturer.name,
    "name": RowItem.title.name,
    "category": RowItem.type_production.name,
}

zapaska_params = ParserParams(
    supplier=ParseParamsSupplier(folder_name="zapaska", name="Запаска (диски)", code="2"),
    start_row=0,
    sheet_info="",
    columns=column_mapping,
    stop_words=[],
    file_templates=["disk.json"],
    sheet_indexes=[],
    row_item_adaptor=RowItem,
)

mark_up_provider = data_provider.MarkupRulesProviderFromUserConfig(zapaska_params.supplier.folder_name)


def get_title_aliases(supplier_name: str) -> dict:
    """Load title aliases for supplier from user config."""
    try:
        return invert_map((json.loads(read_file(MainConfig().title_aliases_file_path)) or {}).get(supplier_name) or {})
    except FileNotFoundError:
        return {}


def invert_map(title_aliases: dict) -> dict:
    """Invert {correct: [incorrect, ...]} to {incorrect: correct}."""
    inverted = {}
    for correct_title, incorrect_titles in title_aliases.items():
        for incorrect_title in incorrect_titles:
            inverted[incorrect_title] = correct_title
    return inverted


zapaska_config = BasePriceParseConfigurationParams(
    markup_rules_provider=mark_up_provider,
    black_list_provider=data_provider.BlackListProviderFromUserConfig(),
    stop_words_provider=data_provider.StopWordsProviderFromUserConfig(),
    vendor_list=data_provider.VendorListProviderFromUserConfig(),
    manufacturer_aliases=data_provider.ManufacturerAliasesProviderFromUserConfig(),
    parser_params=zapaska_params,
)

zapaska_config = ParseConfiguration(zapaska_config)

MIN_RECOMMENDED_MARGIN_PERCENT = 0.08


class ZapaskaDiskJSON(BaseParser):
    """
    Parser rest and price opt for zapaska vendor
    """

    _type_production = "Диск"

    def __init__(self, parse_config, file_prices: list = None):
        """init"""
        self.price_sup_codes = {}
        self.rest_titles = {}
        self.price_mrp_result = []
        self.not_matched_position = []
        self._current_category = None
        self.title_aliases = get_title_aliases(parse_config.parse_config.parser_params.supplier.name)
        super().__init__(parse_config, file_prices)

    def get_price_mrp_result(self) -> List[RowItem]:
        """price mrp result"""
        return self.price_mrp_result

    def raw_parse(self, text_json_file_full_path: str) -> List[dict]:
        """raw parse"""
        with Path(text_json_file_full_path).open(encoding="utf-8") as out_file:
            text_data = out_file.read()
        dictable_data = json.loads(text_data)
        self.rename_fields(dictable_data)
        return dictable_data

    def rename_fields(self, rows: list[dict]):
        """rename fields"""
        columns = self.parse_config().parse_config.parser_params.columns
        for row in rows:
            for column_json, column_price in columns.items():
                if column_json in row:
                    row[column_price] = row.pop(column_json)

    def process(self):
        """parse process"""
        count_processed = super().process()
        self.prepare_prices_mrp()

        for row_item in self.parsed_items:
            self.make_price_markup(row_item)
            self.skip_by_min_rest(row_item)
            row_item.type_production = self.get_type_production(row_item)
            if not row_item.type_production:
                row_item.rest_count = 0
        return count_processed

    def get_type_production(self, row_item: RowItem):
        """Return fixed type production for disk prices."""
        return self._type_production

    def set_rest_and_price_opt(self, rest_result):
        """get parse result for ZapaskaRest"""
        self.price_mrp_result = rest_result

    @classmethod
    def get_item_rest(cls, row_item: RowItem):
        """get rest count"""
        return row_item.rest_count

    def prepare_prices_mrp(self):
        """join result zapaska parser and zapaska rest parser via vendor position code"""
        for price_mrp in self.get_price_mrp_result():
            code = price_mrp.code or price_mrp.code_art

            self.price_sup_codes[code] = price_mrp.price_recommended

    def get_prepared_title(self, row_item: RowItem):
        """Normalize title spaces and apply title aliases."""
        chunks = [chunk.strip() for chunk in row_item.title.split(" ") if chunk.strip()]
        title = " ".join(chunks)
        return self.title_aliases.get(title) or title

    @classmethod
    def _get_price_percent_markup(cls, price):
        """get price percent markup"""
        return next(
            (percent for bounds, percent in cls._percent_map().items() if bounds[0] <= price < bounds[1]),
            _BASE_PERCENT,
        )

    @classmethod
    def _percent_map(cls):
        """Карта наценок по диапазонам цены."""
        step = 0.02
        return {
            (0, 5000): _BASE_PERCENT + step * 5,
            (5000, 10000): _BASE_PERCENT + step * 4,
            (10000, 15000): _BASE_PERCENT + step * 2,
            (15000, 20000): _BASE_PERCENT + step,
            (20000, 25000): _BASE_PERCENT,
        }

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
    def _make_price_recommended_markup(cls, price_recommended, price_opt) -> Tuple[Optional[float], Optional[float]]:
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
        if not cls._is_small_recommended_price(price_recommended, price_opt, percent=MIN_RECOMMENDED_MARGIN_PERCENT):
            return price_recommended, percent

        percent = cls._get_price_percent_markup(price_opt)

        return cls.get_markup(price_opt, percent), percent

    @classmethod
    def _is_small_recommended_price(cls, price_recommended, price_opt, percent) -> bool:
        """check margin for recommended price"""
        return price_recommended and cls.calc_percent(price_recommended, price_opt) <= percent

    def make_price_markup(self, row_item):
        """set markup
        цена закупа от 0 до 5000 прибавляем наценку 17%
        цена закупа от 5000 до 10000 прибавляем наценку 15%
        цена закупа от 10000 до 15000 прибавляем наценку 13%
        цена закупа от 15000 до 20000 прибавляем наценку 10%
        """

        price_recommended = row_item.price_recommended or 0
        price_opt = row_item.price_opt

        if not price_opt:
            return

        if not price_recommended:
            self.not_matched_position.append(row_item.title)

        price_with_markup = self._make_price_markup(price_recommended, price_opt)
        row_item.price_markup = self.round_price(price_with_markup) if price_with_markup else None

    def find_rest_by_title(self, title):
        """find rest by title"""
        if not self.rest_titles:
            for row_item in self.get_price_mrp_result():
                if not row_item.title:
                    continue
                self.rest_titles[row_item.title.lower().strip()] = row_item.price_recommended
        return self.rest_titles.get(title.lower().strip())
