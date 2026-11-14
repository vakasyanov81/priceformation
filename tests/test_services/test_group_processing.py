"""Передача настроек группировки и создание статистики выбранного пакета."""

import logging
from unittest.mock import MagicMock

from domain.product_group_result import TireAndDiskResult
from domain.product_groups import ProductGroup
from domain.row_item.row_item import RowItem
from services.group_processing import group_packages
from services.parse_result import ParseResult


def test_group_packages_passes_reference_priority() -> None:
    """Сборщик получает очередь эталонов; пакет без счётчиков получает статистику группировки."""
    row = RowItem({'title': 'Шина', 'price_opt': 100})
    parsed = ParseResult()
    parsed.add_package(TireAndDiskResult((row,)))
    source = MagicMock()
    source.aliases_map.return_value = {'A': 'B'}
    source.reference_priority.return_value = {'supplier': 1}
    grouper = MagicMock()
    grouper.group_by_params.return_value.get_row_items.return_value = [row]
    grouper.get_double_row_items.return_value = []
    factory = MagicMock(return_value=grouper)

    group_packages(parsed, factory, source, logging.getLogger(__name__))

    factory.assert_called_once_with([row], aliases_map={'A': 'B'}, reference_priority={'supplier': 1})
    assert parsed.tire_and_disk_items == [row]
    counters = parsed.statistics[ProductGroup.TIRE_AND_DISK]
    assert counters.item_count == 1
    assert counters.priced_items == 1
    assert counters.doubles == 0
