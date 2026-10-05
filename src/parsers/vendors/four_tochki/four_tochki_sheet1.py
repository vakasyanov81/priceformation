"""
logic for four_tochki vendor (sheet 1)
"""

import dataclasses

from domain.row_item.row_item import RowItem
from parsers.base_parser.base_parser_config import make_parse_config
from parsers.registry import register_vendor

from .four_tochki_base import FourTochkiParserBase, fourtochki_params
from .four_tochki_title import get_prepared_title

fourtochki_sheet_1_params = dataclasses.replace(
    fourtochki_params,
    sheet_info='Вкладка (шины) #1',
    sheet_indexes=(0,),
    columns={
        0: RowItem.code.name,
        2: RowItem.manufacturer.name,
        3: RowItem.model.name,
        4: RowItem.width.name,
        5: RowItem.height_percent.name,
        6: RowItem.diameter.name,
        7: RowItem.index_load.name,
        8: RowItem.index_velocity.name,
        9: RowItem.season.name,
        10: RowItem.tire_type.name,
        11: RowItem.ext_diameter.name,
        12: RowItem.spike.name,
        13: RowItem.inscription_on_the_side.name,
        14: RowItem.run_flat.name,
        15: RowItem.rest_count.name,
        16: RowItem.price_opt.name,
        17: RowItem.price_recommended.name,
    },
)

fourtochki_sheet_1_config = make_parse_config(fourtochki_sheet_1_params)


@register_vendor('4tochki-1sheet', markup_policy='recommended_or_map')
class FourTochkiParser1Sheet(FourTochkiParserBase):
    """
    parser for four_tochki vendor (sheet 1)
    """

    @classmethod
    def get_current_category(cls, row_item: RowItem) -> str:
        tyre_type_dict = {
            'грузовая': 'Грузовая шина',
            'легковая': 'Легковая шина',
            'спецтехника': 'Спецшина',
            'мото': 'Мотошина',
        }
        tire_type = row_item.tire.tire_type or ''
        return tyre_type_dict.get(tire_type.lower().strip()) or 'Автошина'

    def get_prepared_title(self, row_item: RowItem) -> str:
        return get_prepared_title(row_item)
