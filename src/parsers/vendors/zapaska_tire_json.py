# -*- coding: utf-8 -*-
"""
logic for zapaska (rest) vendor
"""
__author__ = "Kasyanov V.A."

from .zapaska_disk_json import ZapaskaDiskJSON
from .. import data_provider
from ..base_parser.base_parser_config import (
    ParserParams,
    ParseParamsSupplier,
    BasePriceParseConfigurationParams,
    ParseConfiguration,
)
from ..row_item.row_item import RowItem

zapaska_tire_params = ParserParams(
    supplier=ParseParamsSupplier(folder_name="zapaska", name="Запаска (шины)", code="22"),
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
    },
    stop_words=[],
    file_templates=["tire.json"],
    sheet_indexes=[],
    row_item_adaptor=RowItem,
)

mark_up_provider = data_provider.MarkupRulesProviderFromUserConfig(zapaska_tire_params.supplier.folder_name)

zapaska_tire_config = BasePriceParseConfigurationParams(
    markup_rules_provider=mark_up_provider,
    black_list_provider=data_provider.BlackListProviderFromUserConfig(),
    stop_words_provider=data_provider.StopWordsProviderFromUserConfig(),
    vendor_list=data_provider.VendorListProviderFromUserConfig(),
    manufacturer_aliases=data_provider.ManufacturerAliasesProviderFromUserConfig(),
    parser_params=zapaska_tire_params,
)

zapaska_tire_config = ParseConfiguration(zapaska_tire_config)


class ZapaskaTireJSON(ZapaskaDiskJSON):
    """
    Parser rest and price opt for zapaska vendor
    """

    @classmethod
    def get_prepared_title(cls, item: RowItem):
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
