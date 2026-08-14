"""
logic for mim vendor (sheet 2)
"""

import dataclasses
from typing import Any

from parsers.row_item.row_item import RowItem

from ... import data_provider
from ...base_parser.base_parser_config import (
    BasePriceParseConfigurationParams,
    ParseConfiguration,
)
from .mim_base import MimParserBase, mim_params, supplier_folder_name

TRUCK_TIRE_PRICE_THRESHOLD = 13000
TRUCK_TIRE_MARKUP_LOW = 0.07
TRUCK_TIRE_MARKUP_HIGH = 0.05

mim_sheet_2_params = dataclasses.replace(mim_params)
mim_sheet_2_params.sheet_info = "Вкладка #2"
mim_sheet_2_params.sheet_indexes = [1]
mim_sheet_2_params.columns = {
    0: RowItem.code.name,
    1: RowItem.title.name,
    3: RowItem.manufacturer.name,
    4: RowItem.model.name,
    6: RowItem.width.name,
    7: RowItem.height_percent.name,
    8: RowItem.construction_type.name,
    9: RowItem.diameter.name,
    11: RowItem.axis.name,
    12: RowItem.intimacy.name,
    13: RowItem.layering.name,
    14: RowItem.index_load.name,
    15: RowItem.index_velocity.name,
    20: RowItem.rest_count.name,
    22: RowItem.price_opt.name,
    23: RowItem.price_recommended.name,
}

mark_up_provider = data_provider.MarkupRulesProviderFromUserConfig(supplier_folder_name)

mim_sheet_2_config = ParseConfiguration(
    BasePriceParseConfigurationParams(
        markup_rules_provider=mark_up_provider,
        black_list_provider=data_provider.BlackListProviderFromUserConfig(),
        stop_words_provider=data_provider.StopWordsProviderFromUserConfig(),
        vendor_list=data_provider.VendorListProviderFromUserConfig(),
        manufacturer_aliases=data_provider.ManufacturerAliasesProviderFromUserConfig(),
        parser_params=mim_sheet_2_params,
    )
)


class MimParser2Sheet(MimParserBase):
    """
    parser for mim vendor (sheet 2)
    """

    @classmethod
    def get_current_category(cls) -> str:
        """current category"""
        return "Грузовая шина"

    def get_markup_percent(self, price_value: float) -> float:
        """Для грузовых позиций наценка"""
        # TODO: добавить настройку наценок для грузовой шины в настройки
        if price_value <= TRUCK_TIRE_PRICE_THRESHOLD:
            return TRUCK_TIRE_MARKUP_LOW
        return TRUCK_TIRE_MARKUP_HIGH

    def add_price_markup(self, row_item: RowItem) -> None:
        price_opt = row_item.price_opt or 0
        price = self.get_markup(price_opt, self.get_markup_percent(price_opt))
        row_item.price_markup = self.round_price(price)

    @classmethod
    def get_prepared_title(cls, row_item: RowItem) -> str:
        """prepare title"""
        return " ".join(cls._title_chunks(row_item))

    @classmethod
    def _size_chunk(cls, row_item: RowItem) -> str:
        """Кусок размера width/profileRdiameter."""
        profile = "/{0}".format(row_item.height_percent) if row_item.height_percent else ""
        diameter = "R{0}".format(row_item.diameter) if row_item.diameter else ""
        return "".join((str(row_item.width or ""), profile, diameter))

    @classmethod
    def _title_chunks(cls, row_item: RowItem) -> list[str]:
        """Ненулевые части title."""
        mark = (row_item.manufacturer or "").lower().capitalize()
        load_vel = "{0}{1}".format(row_item.index_load or "", row_item.index_velocity or "")
        raw = [
            cls._size_chunk(row_item),
            mark,
            row_item.model,
            row_item.layering,
            load_vel,
            row_item.intimacy,
            row_item.axis,
        ]
        return cls._nonempty_chunks(raw)

    @classmethod
    def _nonempty_chunks(cls, raw: list[Any]) -> list[str]:
        """Оставить только непустые части title."""
        cleaned = []
        for chunk in raw:
            text = str(chunk or "").strip()
            if text:
                cleaned.append(text)
        return cleaned
