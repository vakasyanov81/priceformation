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
from parsers.row_item.row_item_formatter import get_try_to_int_or_str

from .four_tochki_base import FourTochkiParserBase, fourtochki_params

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

    def add_price_markup(self, row_item: RowItem) -> None:
        if row_item.price_recommended:
            price = row_item.price_recommended
        else:
            price_opt = row_item.price_opt or 0
            price = self.get_markup(price_opt, self.get_markup_percent(price_opt))
        row_item.price_markup = self.round_price(price)

    @classmethod
    def get_prepared_title(cls, row_item: RowItem) -> str:
        return get_prepared_title(row_item)


def get_prepared_title(row_item: RowItem) -> str:
    """
    1) Форточки:
    10-20 Armour TI300
    на
    10.00-20 Armour TI300 16PR TTF

    2). Форточки:
    10/75-15.3 Forerunner QH602 R-4
    на
    10.0/75-15.3 Forerunner QH602 R-4 12PR TL

    3) Форточки:
    11/999-15 Galaxy Rib Implement I-1
    на
    11L-15 Galaxy Rib Implement I-1 12PR TL

    4) МИМ:
    16.5/70R18 Белшина КФ-97 10 149A TTF
    на
    16.5/70-18 Белшина КФ-97 10 149A TTF
    :param item:
    :return:
    """
    dims = _prepare_dimensions(row_item)
    return _compose_title(row_item, dims).strip()


def _prepare_dimensions(row_item: RowItem) -> tuple[str, str, str, str]:
    """Ширина, профиль, диаметр и тип конструкции."""
    width = str(get_try_to_int_or_str(row_item.width or ""))
    height = get_try_to_int_or_str(str(row_item.height_percent or "").replace("999", "L"))
    diameter = str((row_item.diameter or "").replace("—", "-")).replace("R", "")
    construct = "R"
    if "-" in diameter:
        construct = "-"
        diameter = diameter.replace("-", "")
    return width, str(height), diameter, construct


def _compose_title(row_item: RowItem, dims: tuple[str, str, str, str]) -> str:
    """Собрать title по типу шины. dims: width, height_raw, diameter, construct."""
    height = f"/{dims[1]}" if dims[1] and dims[1] != "L" else ""
    postfix = _resolve_width_postfix(row_item, dims[0], dims[1], dims[2])
    construct_diameter = f"{dims[3]}{dims[2]}".replace("RZ", "ZR")
    return _pick_title(row_item, (dims[0], height, postfix, construct_diameter))


def _pick_title(row_item: RowItem, parts: tuple[str, str, str, str]) -> str:
    """Выбрать шаблон title. parts: width, height, postfix, construct_diameter."""
    mark = (row_item.manufacturer or "").lower().capitalize()
    if is_truck_tire(row_item):
        return _truck_title(row_item, parts, mark)
    if row_item.ext_diameter:
        return _ext_diameter_title(row_item, parts, mark)
    return _default_tire_title(row_item, parts, mark)


def _ext_diameter_title(row_item: RowItem, parts: tuple[str, str, str, str], mark: str) -> str:
    """Title с внешним диаметром."""
    size = "{0}x{1}{2}".format(row_item.ext_diameter, parts[0], parts[3])
    return " ".join(
        (size, mark, row_item.model or "", row_item.index_load or "", row_item.us_aff_designation or ""),
    )


def _truck_title(row_item: RowItem, parts: tuple[str, str, str, str], mark: str) -> str:
    """Title для грузовой шины."""
    size = "".join((parts[0], parts[2], parts[1], parts[3]))
    load_vel = "{0}{1}".format(row_item.index_load or "", row_item.index_velocity or "")
    return " ".join((size, mark, row_item.model or "", load_vel))


def _default_tire_title(row_item: RowItem, parts: tuple[str, str, str, str], mark: str) -> str:
    """Обычный title легковой/спец."""
    size = "".join((parts[0], parts[2], parts[1], parts[3]))
    load_vel = "{0}{1}".format(row_item.index_load or "", row_item.index_velocity or "")
    return " ".join(
        (size, mark, row_item.model or "", row_item.layering or "", row_item.camera_type or "", load_vel),
    )


def _resolve_width_postfix(row_item: RowItem, width: str, height_percent: str, diameter: str) -> str:
    """подбирает суффикс ширины для title"""
    # 205/55R16 BFGoodrich Advantage 94W
    # 30x9,5R15 BFGoodrich All Terrain T/A KO2 104S LT
    width_postfix = ""
    if is_truck_tire(row_item):
        width_postfix = ".00"
    if diameter == "22.5" or height_percent:
        width_postfix = ""
    if is_truck_tire(row_item) and diameter == "16":
        width_postfix = ""
    if width == "10" and diameter == "20":
        width_postfix = ".00"

    if is_special_tire(row_item) and height_percent and height_percent != "L" and "." not in width:
        width_postfix = ".0"

    if height_percent == "L":
        width_postfix = height_percent

    return width_postfix


def is_truck_tire(row_item: RowItem) -> bool:
    """Грузовая шина?"""
    return row_item.tire_type.lower() == "грузовая" if row_item.tire_type else False


def is_special_tire(row_item: RowItem) -> bool:
    """Спецтехника?"""
    return row_item.tire_type.lower() == "спецтехника" if row_item.tire_type else False
