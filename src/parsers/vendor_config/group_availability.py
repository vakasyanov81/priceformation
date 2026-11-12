"""Предварительная проверка готовности объявленных аккумуляторных секций."""

from domain.exceptions import ConfigValidationError
from parsers.vendor_config.group_models import BatterySection
from parsers.vendor_config.models import VendorConfig

REQUIRED_COLUMNS = frozenset(('code', 'title', 'price_recommended', 'rest_count'))


def ensure_battery_section(section: BatterySection) -> None:
    """Проверить обязательные отображения до обработки файлов."""
    missing = REQUIRED_COLUMNS - set(section.columns.values())
    if missing:
        raise ConfigValidationError(f'{section.config_path} → columns: отсутствуют поля batteries {sorted(missing)}')


def ensure_groups_available(config: VendorConfig) -> None:
    """Проверить все выбранные секции активного поставщика."""
    if config.enabled:
        for section in config.all_sections:
            if isinstance(section, BatterySection):
                ensure_battery_section(section)


def ensure_section_available(config: VendorConfig, code: str) -> None:
    """Явный выбор секции проверяет только её настройки."""
    for section in config.all_sections:
        if section.id == code and isinstance(section, BatterySection):
            ensure_battery_section(section)
