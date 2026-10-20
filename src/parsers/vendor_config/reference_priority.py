"""Очередь поставщиков-эталонов названия: имя поставщика в позиции прайса → место в очереди (1 — первый)."""

from parsers.vendor_config.provider import load_vendor_configs


def load_reference_priority() -> dict[str, int]:
    """Места из ``title.reference_priority`` конфигов; поставщики без места в карту не попадают."""
    priority: dict[str, int] = {}
    for config in load_vendor_configs().values():
        rank = config.title.reference_priority
        if rank > 0:
            priority[config.name] = rank
            priority.update({section.name: rank for section in config.sections})
    return priority
