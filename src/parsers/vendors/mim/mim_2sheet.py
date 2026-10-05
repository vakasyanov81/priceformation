"""
logic for mim vendor (sheet 2)
"""

import dataclasses

from domain.row_item.row_item import RowItem
from parsers.nomenclature_title import compose_tire_title, join_size_parts, load_velocity
from parsers.registry import register_vendor

from ...base_parser.base_parser_config import make_parse_config
from .mim_base import MimParserBase, mim_params

TRUCK_TIRE_PRICE_THRESHOLD = 13000
TRUCK_TIRE_MARKUP_LOW = 0.07
TRUCK_TIRE_MARKUP_HIGH = 0.05

mim_sheet_2_params = dataclasses.replace(
    mim_params,
    sheet_info='Вкладка #2',
    sheet_indexes=(1,),
    columns={
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
    },
)

mim_sheet_2_config = make_parse_config(mim_sheet_2_params)


@register_vendor('mim-2sheet', markup_policy=None)
class MimParser2Sheet(MimParserBase):
    """
    parser for mim vendor (sheet 2)
    """

    @classmethod
    def get_current_category(cls) -> str:
        """current category"""
        return 'Грузовая шина'

    def get_markup_percent(self, price_value: float) -> float:
        """Для грузовых позиций наценка"""
        # TODO: добавить настройку наценок для грузовой шины в настройки
        if price_value <= TRUCK_TIRE_PRICE_THRESHOLD:
            return TRUCK_TIRE_MARKUP_LOW
        return TRUCK_TIRE_MARKUP_HIGH

    def add_price_markup(self, row_item: RowItem) -> None:
        price_opt = row_item.pricing.price_opt or 0
        price = self.get_markup(price_opt, self.get_markup_percent(price_opt))
        row_item.set_field('price_markup', self.round_price(price))

    def get_prepared_title(self, row_item: RowItem) -> str:
        """prepare title"""
        height_percent = row_item.tire.height_percent or ''
        diameter = row_item.tire.diameter or ''
        profile = f'/{height_percent}' if height_percent else ''
        size = join_size_parts(row_item.tire.width, profile, f'R{diameter}' if diameter else '')
        return compose_tire_title(
            row_item,
            size,
            row_item.tire.layering,
            load_velocity(row_item),
            row_item.tire.intimacy,
            row_item.tire.axis,
        )
