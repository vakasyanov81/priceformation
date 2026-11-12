"""Сборка аккумуляторного обработчика; не снимает запрет запуска до полного сценария 8.6."""

from domain.exceptions import ConfigValidationError
from parsers.battery.handler import BatteryHandler
from parsers.vendor_config.group_models import BatterySection

REQUIRED_COLUMNS = frozenset(('code', 'title', 'price_recommended', 'rest_count'))


def make_battery_handler(section: BatterySection, supplier: str) -> BatteryHandler:
    """Проверить полноту отображения перед чтением файлов и собрать обработчик группы."""
    missing = REQUIRED_COLUMNS - set(section.columns.values())
    if missing:
        raise ConfigValidationError(f'{section.config_path} → columns: отсутствуют поля batteries {sorted(missing)}')
    return BatteryHandler(section.processing, supplier)
