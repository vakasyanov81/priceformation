"""Сборка парсера поставщика из записи реестра."""

from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.base_parser_config import ParseConfiguration
from parsers.base_parser.config_driven_parser import make_config_driven_parser


def parser_for_vendor(vendor_cls: type[BaseParser], vendor_config: ParseConfiguration | None) -> BaseParser:
    """Собрать config-driven парсер поставщика."""
    if vendor_config is None or not vendor_config.is_enabled:
        return vendor_cls(parse_config=vendor_config)
    section = vendor_config.vendor_section
    vendor_cfg = vendor_config.vendor_config
    if section is None or vendor_cfg is None:
        return vendor_cls(parse_config=vendor_config)
    return make_config_driven_parser(section, vendor_cfg, vendor_config)
