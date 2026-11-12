"""Общие параметры чтения секций независимых товарных моделей."""

from parsers.base_parser.base_parser_config import ParseParamsSupplier, ParserParams
from parsers.vendor_config.group_models import BatterySection
from parsers.vendor_config.section_models import VendorSection


def parser_params_from_section(section: VendorSection | BatterySection, folder: str) -> ParserParams:
    """Собрать ``ParserParams`` из секции конфига.

    Args:
        section: Секция поставщика (один лист/файл).
        folder: Имя папки поставщика (``file_prices/<folder>/``).
    """
    return ParserParams(
        supplier=ParseParamsSupplier(folder_name=folder, name=section.name, code=section.id),
        start_row=section.start_row,
        sheet_info=section.sheet_info,
        columns=dict(section.columns.items()),
        stop_words=(),
        file_templates=section.file_templates,
        sheet_indexes=section.sheet_indexes,
    )
