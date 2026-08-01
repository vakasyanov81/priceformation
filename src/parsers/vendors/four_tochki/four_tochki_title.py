"""Title builders for four_tochki sheet 1 tires."""

from parsers.row_item.row_item import RowItem
from parsers.row_item.row_item_casts import get_try_to_int_or_str

from .four_tochki_title_parts import default_tire_title, ext_diameter_title, truck_title

_PROFILE_L = "L"
_DASH = "-"


def is_truck_tire(row_item: RowItem) -> bool:
    """Грузовая шина?"""
    return row_item.tire_type.lower() == "грузовая" if row_item.tire_type else False


def is_special_tire(row_item: RowItem) -> bool:
    """Спецтехника?"""
    return row_item.tire_type.lower() == "спецтехника" if row_item.tire_type else False


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
    percent = str(row_item.height_percent or "")
    height = get_try_to_int_or_str(percent.replace("999", _PROFILE_L))
    diameter = str(row_item.diameter or "").replace("—", _DASH)
    diameter = diameter.replace("R", "")
    construct = "R"
    if _DASH in diameter:
        construct = _DASH
        diameter = diameter.replace(_DASH, "")
    return width, str(height), diameter, construct


def _profile_slash(height_value: str) -> str:
    """Префикс профиля для title, пусто для L-профиля."""
    if not height_value or height_value == _PROFILE_L:
        return ""
    return f"/{height_value}"


def _compose_title(row_item: RowItem, dims: tuple[str, str, str, str]) -> str:
    """Собрать title по типу шины. dims: width, height_raw, diameter, construct."""
    height = _profile_slash(dims[1])
    postfix = _resolve_width_postfix(row_item, dims[0], dims[1], dims[2])
    construct_diameter = f"{dims[3]}{dims[2]}".replace("RZ", "ZR")
    parts = (dims[0], height, postfix, construct_diameter)
    mark = (row_item.manufacturer or "").lower().capitalize()
    if is_truck_tire(row_item):
        return truck_title(row_item, parts, mark)
    if row_item.ext_diameter:
        return ext_diameter_title(row_item, parts, mark)
    return default_tire_title(row_item, parts, mark)


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

    if is_special_tire(row_item) and height_percent and height_percent != _PROFILE_L and "." not in width:
        width_postfix = ".0"

    if height_percent == _PROFILE_L:
        width_postfix = height_percent

    return width_postfix
