"""
logic for mim vendor (sheet 2)
"""

import dataclasses

from parsers.row_item.row_item import RowItem
from .mim_base import MimParserBase, mim_params, supplier_folder_name
from ... import data_provider
from ...base_parser.base_parser_config import (
    BasePriceParseConfigurationParams,
    ParseConfiguration,
)


def config_for_sheets2():
    """get config for sheets 2 parsers"""
    return dict(
        {
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
            23: RowItem.price_recommended,
        }
    )


mim_sheet_2_params = dataclasses.replace(mim_params)
mim_sheet_2_params.sheet_info = "Вкладка #2"
mim_sheet_2_params.sheet_indexes = [1]
mim_sheet_2_params.columns = config_for_sheets2()

mark_up_provider = data_provider.MarkupRulesProviderFromUserConfig(supplier_folder_name)

mim_sheet_2_config = BasePriceParseConfigurationParams(
    markup_rules_provider=mark_up_provider,
    black_list_provider=data_provider.BlackListProviderFromUserConfig(),
    stop_words_provider=data_provider.StopWordsProviderFromUserConfig(),
    vendor_list=data_provider.VendorListProviderFromUserConfig(),
    manufacturer_aliases=data_provider.ManufacturerAliasesProviderFromUserConfig(),
    parser_params=mim_sheet_2_params,
)

mim_sheet_2_config = ParseConfiguration(mim_sheet_2_config)


class MimParser2Sheet(MimParserBase):
    """
    parser for mim vendor (sheet 2)
    """

    @classmethod
    def get_current_category(cls):
        """current category"""
        return "Грузовая шина"

    def get_markup_percent(self, price_value: float):
        """Для грузовых позиций наценка"""
        # TODO: добавить настройку наценок для грузовой шины в настройки
        if price_value <= 13000:
            return 0.07
        return 0.05

    def add_price_markup(self, item: RowItem):
        price_opt = item.price_opt or 0
        price = self.get_markup(price_opt, self.get_markup_percent(price_opt))
        item.price_markup = self.round_price(price)

    @classmethod
    def get_prepared_title(cls, item: RowItem):
        """prepare title"""
        width = item.width or ""
        diameter = item.diameter or ""
        profile = item.height_percent or ""
        velocity = item.index_velocity or ""
        load = item.index_load or ""
        mark = (item.manufacturer or "").lower().capitalize()
        model = item.model or ""
        axis = item.axis or ""
        layering = item.layering or ""
        intimacy = item.intimacy or ""

        if profile:
            profile = f"/{profile}"

        if diameter:
            diameter = f"R{diameter}"

        chunks = [
            f"{width}{profile}{diameter}",
            mark,
            model,
            layering,
            f"{load}{velocity}",
            intimacy,
            axis,
        ]

        chunks = [str(chunk or "").strip() or None for chunk in chunks]

        chunks = [chunk for chunk in chunks if chunk]

        title = " ".join(chunks)

        return title
