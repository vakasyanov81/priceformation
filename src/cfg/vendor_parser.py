"""Композиция парсеров независимых товарных моделей."""

from cfg.battery import make_battery_handler
from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.base_parser_config import ParseConfiguration
from parsers.base_parser.supplier_parser import SupplierParser
from parsers.battery.parser import BatteryParser
from parsers.vendor_config.group_models import BatterySection
from services.vendor_parser import parser_for_vendor as tire_parser_for_vendor


def parser_for_vendor(vendor_cls: type[BaseParser], vendor_config: ParseConfiguration | None) -> SupplierParser:
    """Собрать модель и её стратегии до чтения прайсов."""
    if vendor_config is not None and isinstance(vendor_config.vendor_section, BatterySection):
        section = vendor_config.vendor_section
        return BatteryParser(vendor_config, make_battery_handler(section, section.name))
    return tire_parser_for_vendor(vendor_cls, vendor_config)
