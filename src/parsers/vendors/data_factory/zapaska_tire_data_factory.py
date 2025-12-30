from parsers.base_parser.base_parser_config import BasePriceParseConfigurationParams, ParseConfiguration, ParseParamsSupplier, ParserParams
from parsers.vendors.zapaska_disk import column_mapping
from parsers.row_item.row_item import RowItem
from parsers import data_provider


def _get_vendor_params(vendor_name: str = "zapaska", column_mapping: dict = {}):
    column_mapping = dict(column_mapping)
    column_mapping.update(
        {
            "height": RowItem.__HEIGHT_PERCENT__,
            "load_index": RowItem.__INDEX_LOAD__,
            "speed_index": RowItem.__INDEX_VELOCITY__,
            "studded": RowItem.__SPIKE__,
        }
    )
    zapaska_tire_params = ParserParams(
        supplier=ParseParamsSupplier(folder_name="zapaska", name="Запаска (шины)", code="22"),
        start_row=0,
        sheet_info="",
        columns=column_mapping,
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
    
    return ParserParams(
        supplier=ParseParamsSupplier(folder_name=vendor_name, name="Запаска (шины)", code="22"),
        start_row=0,
        sheet_info="",
        columns=column_mapping,
        stop_words=[],
        file_templates=["tire.json"],
        sheet_indexes=[],
        row_item_adaptor=RowItem,
    )


def _get_vendor_config(vendor_name: str = "zapaska", column_mapping: dict = {}):

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
    
    return zapaska_tire_config
def get_vendor_params():
    return _get_vendor_params(column_mapping=column_mapping)
