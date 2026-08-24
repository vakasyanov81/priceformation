"""
logic for four_tochki vendor (sheet 1)
"""

import dataclasses

from parsers import data_provider
from parsers.base_parser.base_parser_config import (
    BasePriceParseConfigurationParams,
    ParseConfiguration,
)
from parsers.row_item.row_item import RowItem

from .four_tochki_base import FourTochkiParserBase, fourtochki_params
from .four_tochki_title import get_prepared_title

fourtochki_sheet_1_params = dataclasses.replace(fourtochki_params)
fourtochki_sheet_1_params.sheet_info = "Вкладка (шины) #1"
fourtochki_sheet_1_params.sheet_indexes = [0]
fourtochki_sheet_1_params.columns = {
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
    15: RowItem.us_aff_designation.name,
    16: RowItem.camera_type.name,
    17: RowItem.axis.name,
    18: RowItem.layering.name,
    19: RowItem.construction_type.name,
    20: RowItem.rest_count.name,
    21: RowItem.price_recommended.name,
    22: RowItem.price_opt.name,
}

supplier_folder_name = fourtochki_params.supplier.folder_name

mark_up_provider = data_provider.MarkupRulesProviderFromUserConfig(supplier_folder_name)

fourtochki_sheet_1_config = ParseConfiguration(
    BasePriceParseConfigurationParams(
        markup_rules_provider=mark_up_provider,
        black_list_provider=data_provider.BlackListProviderFromUserConfig(),
        stop_words_provider=data_provider.StopWordsProviderFromUserConfig(),
        vendor_list=data_provider.VendorListProviderFromUserConfig(),
        manufacturer_aliases=data_provider.ManufacturerAliasesProviderFromUserConfig(),
        parser_params=fourtochki_sheet_1_params,
    )
)


class FourTochkiParser1Sheet(FourTochkiParserBase):
    """
    parser for four_tochki vendor (sheet 1)
    """

    @classmethod
    def get_current_category(cls, row_item: RowItem) -> str:
        tyre_type_dict = {
            "грузовая": "Грузовая шина",
            "легковая": "Легковая шина",
            "спецтехника": "Спецшина",
            "мото": "Мотошина",
        }
        return tyre_type_dict.get(row_item.tire_type.lower().strip()) or "Автошина"

    @classmethod
    def get_prepared_title(cls, row_item: RowItem) -> str:
        return get_prepared_title(row_item)
