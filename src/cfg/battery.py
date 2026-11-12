"""Сборка аккумуляторного обработчика с проверкой обязательных колонок."""

from parsers.battery.handler import BatteryHandler
from parsers.vendor_config.group_availability import ensure_battery_section
from parsers.vendor_config.group_models import BatterySection


def make_battery_handler(section: BatterySection, supplier: str) -> BatteryHandler:
    """Проверить полноту отображения перед чтением файлов и собрать обработчик группы."""
    ensure_battery_section(section)
    return BatteryHandler(section.processing, supplier)
