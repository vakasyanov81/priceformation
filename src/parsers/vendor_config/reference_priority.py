"""Очередь поставщиков-эталонов названия: имя поставщика в позиции прайса → место в очереди (1 — первый)."""

from domain.exceptions import ConfigValidationError
from parsers.vendor_config.provider import load_common_settings, load_vendor_configs

_WHERE = '_common.json → title_reference_order'


def load_reference_priority() -> dict[str, int]:
    """Места из ``title_reference_order`` общих настроек; поставщики вне очереди в карту не попадают."""
    configs = load_vendor_configs()
    priority: dict[str, int] = {}
    for rank, folder in enumerate(load_common_settings().title_reference_order, start=1):
        config = configs.get(folder)
        if config is None:
            raise ConfigValidationError(f'{_WHERE}: нет поставщика «{folder}» (ожидается имя файла из vendors/)')
        priority[config.name] = rank
        priority.update({section.name: rank for section in config.sections})
    return priority
