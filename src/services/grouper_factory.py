"""Фабрика группировщика с приоритетными поставщиками из ``doubles.json``."""

from collections.abc import Mapping
from typing import Any

from domain.config_context import get_config_provider
from domain.row_item.row_item import RowItem
from parsers.common_price.grouper import CommonPriceGrouper
from parsers.data_provider.doubles_settings import load_doubles_settings
from parsers.writer.templates.all_templates import writer_templates_by_name


def grouper_factory(
    row_items: list[RowItem],
    *,
    aliases_map: dict[str, Any],
    reference_priority: Mapping[str, int],
) -> CommonPriceGrouper:
    """Группировщик с приоритетными поставщиками на момент разбора."""
    return CommonPriceGrouper(row_items, aliases_map, reference_priority, _priority_suppliers())


def _priority_suppliers() -> tuple[str, ...]:
    """Приоритетные поставщики из ``doubles.json``; файла нет — пусто."""
    settings = load_doubles_settings(tuple(writer_templates_by_name()), get_config_provider())
    return settings.priority_suppliers
