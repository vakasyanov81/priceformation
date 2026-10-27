"""Сборка парсера поставщика из записи реестра."""

from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.base_parser_config import ParseConfiguration
from parsers.base_parser.config_driven_parser import make_config_driven_parser
from parsers.registry import vendor_config_is_enabled
from parsers.vendor_config.models import VendorConfig as _VendorConfig
from parsers.vendor_config.models import VendorSection as _VendorSection


def parser_for_vendor(vendor_cls: type[BaseParser], vendor_config: ParseConfiguration | None) -> BaseParser:
    """Собрать config-driven парсер поставщика."""
    if vendor_config is None or not vendor_config_is_enabled(vendor_config):
        return vendor_cls(parse_config=vendor_config)
    section = getattr(vendor_config, '_vendor_section', None)
    vendor_cfg = getattr(vendor_config, '_vendor_config', None)
    if isinstance(section, _VendorSection) and isinstance(vendor_cfg, _VendorConfig):
        return make_config_driven_parser(section, vendor_cfg, vendor_config)
    return vendor_cls(parse_config=vendor_config)
