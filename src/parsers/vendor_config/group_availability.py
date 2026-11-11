"""Предварительный отказ для объявленной, но ещё не реализованной группы."""

from domain.exceptions import ConfigValidationError
from parsers.vendor_config.group_models import BatteryConfig
from parsers.vendor_config.models import VendorConfig


def ensure_groups_available(config: VendorConfig) -> None:
    """Запуск всех групп не должен молча выдавать только шинный результат."""
    if config.enabled:
        for group in config.product_groups:
            if isinstance(group, BatteryConfig):
                _unavailable(config)


def ensure_section_available(config: VendorConfig, code: str) -> None:
    """Явный выбор шинной секции не активирует соседнюю группу аккумуляторов."""
    for group in config.product_groups:
        if not isinstance(group, BatteryConfig):
            continue
        if any(section.id == code for section in group.sections):
            _unavailable(config)


def _unavailable(config: VendorConfig) -> None:
    """Ошибка содержит поставщика и стабильный идентификатор группы."""
    raise ConfigValidationError(f'{config.folder}.json: обработка группы batteries ещё недоступна')
