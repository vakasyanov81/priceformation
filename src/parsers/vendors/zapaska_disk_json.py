# -*- coding: utf-8 -*-
"""
logic for zapaska (rest) vendor
"""
__author__ = "Kasyanov V.A."

import json
from typing import List, Optional, Tuple

from src.cfg.main import MainConfig
from src.core.file_reader import read_file
from src.parsers import data_provider
from src.parsers.base_parser.base_parser import BaseParser
from src.parsers.base_parser.base_parser_config import (
    BasePriceParseConfigurationParams,
    ParseConfiguration,
    ParseParamsSupplier,
    ParserParams,
)
from src.parsers.row_item.row_item import RowItem

zapaska_params = ParserParams(
    supplier=ParseParamsSupplier(folder_name="zapaska", name="Запаска (диски)", code="2"),
    start_row=0,
    sheet_info="",
    columns={
        RowItem.__CODE__: RowItem.__CODE__,
        "cae": RowItem.__CODE_ART__,
        "rest": RowItem.__REST_COUNT__,
        "price": RowItem.__PRICE_PURCHASE__,
        "retail": RowItem.__PRICE_RECOMMENDED__,
        "diam_center": RowItem.__CENTRAL_DIAMETER__,
        "holes": RowItem.__SLOT_COUNT__,
        "diam_holes": RowItem.__SLOT_DIAMETER__,
        "ET": RowItem.__ET__,
        "brand": RowItem.__MANUFACTURER_NAME__,
        "name": RowItem.__TITLE__,
    },
    stop_words=[],
    file_templates=["disk.json"],
    sheet_indexes=[],
    row_item_adaptor=RowItem,
)

mark_up_provider = data_provider.MarkupRulesProviderFromUserConfig(zapaska_params.supplier.folder_name)


def get_title_aliases(supplier_name: str) -> dict:
    try:
        return invert_map((json.loads(read_file(MainConfig().title_aliases_file_path)) or {}).get(supplier_name) or {})
    except FileNotFoundError:
        return {}


def invert_map(title_aliases: dict) -> dict:
    result = {}
    for correct_title, incorrect_titles in title_aliases.items():
        for incorrect_title in incorrect_titles:
            result[incorrect_title] = correct_title
    return result


zapaska_config = BasePriceParseConfigurationParams(
    markup_rules_provider=mark_up_provider,
    black_list_provider=data_provider.BlackListProviderFromUserConfig(),
    stop_words_provider=data_provider.StopWordsProviderFromUserConfig(),
    vendor_list=data_provider.VendorListProviderFromUserConfig(),
    manufacturer_aliases=data_provider.ManufacturerAliasesProviderFromUserConfig(),
    parser_params=zapaska_params,
)

zapaska_config = ParseConfiguration(zapaska_config)


class ZapaskaDiskJSON(BaseParser):
    """
    Parser rest and price opt for zapaska vendor
    """

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

    def raw_parse(self, _file: str) -> List[dict]:
        """raw parse"""
        with open(_file, "r", encoding="utf-8") as file_:
            data = file_.read()
        data = json.loads(data)
        self.rename_fields(data)
        return data

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

        for item in self.result:
            if self.is_category_row(item):
                current_category, _ = self._category_finder.find(item)
                self._current_category = current_category or self._current_category
            else:
                item.type_production = self._current_category

            self.make_price_markup(item)
            self.skip_by_min_rest(item)

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

    def get_prepared_title(self, item: RowItem):
        chunks = [chunk.strip() for chunk in item.title.split(" ") if chunk.strip()]
        title = " ".join(chunks)
        return self.title_aliases.get(title) or title

    @classmethod
    def get_prepared_title_new(cls, item: RowItem):
        """get prepared title"""
        width = item.width or ""
        diameter = item.diameter or ""
        model = item.model or ""
        slot_count = item.slot_count or ""
        dia = item.central_diameter or ""
        slot_diameter = item.slot_diameter or ""
        color = item.color or ""
        _et = item.eet or ""
        brand = item.brand or ""
        mark = (item.manufacturer or "").lower().capitalize()

        # 6,5x16 5x114,3 ET45 60,1 MBMF Alcasta M35
        title = f"{brand} {model} {width}*{diameter} {slot_count}*{slot_diameter} ET{_et} D{dia} {color} {mark}"

        # Replay HND369 7.5*20 5*114.3 ET49.5 D67.1 MGMF
        # brand model width * diameter holes * diam_holes ET{et} D{diam_center} color
        return title

    @classmethod
    def is_truck_tire(cls, item: RowItem):
        """Грузовая шина?"""
        return item.tire_type.lower() == "грузовая"

    @classmethod
    def is_special_tire(cls, item: RowItem):
        """Спецтехника?"""
        return item.tire_type.lower() == "спецтехника"

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
        if not cls._is_small_recommended_price(price_recommended, price_opt, percent=0.08):
            return price_recommended, percent

        percent = cls._get_price_percent_markup(price_opt)

        return cls.get_markup(price_opt, percent), percent

    @classmethod
    def _is_small_recommended_price(cls, price_recommended, price_opt, percent) -> bool:
        """check margin for recommended price"""
        return price_recommended and cls.calc_percent(price_recommended, price_opt) <= percent

    def make_price_markup(self, item):
        """set markup
        цена закупа от 0 до 5000 прибавляем наценку 17%
        цена закупа от 5000 до 10000 прибавляем наценку 15%
        цена закупа от 10000 до 15000 прибавляем наценку 13%
        цена закупа от 15000 до 20000 прибавляем наценку 10%
        """
        code = item.code or item.code_art

        price_recommended = self.price_sup_codes.get(code) or self.find_rest_by_title(item.title)
        price_recommended = price_recommended or 0
        price_opt = item.price_opt

        if price_recommended:
            item.price_recommended = price_recommended

        if not price_opt:
            return

        if not price_recommended:
            self.not_matched_position.append(item.title)

        price_with_markup = self._make_price_markup(price_recommended, price_opt)
        item.price_markup = self.round_price(price_with_markup) if price_with_markup else None

    def find_rest_by_title(self, title):
        """find rest by title"""
        if not self.rest_titles:
            for item in self.get_price_mrp_result():
                if not item.title:
                    continue
                self.rest_titles[item.title.lower().strip()] = item.price_recommended
        return self.rest_titles.get(title.lower().strip())
