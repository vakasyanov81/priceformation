"""Правила группировки пакетов конкретных моделей и обновление общих счётчиков."""

import logging
from typing import TYPE_CHECKING

from domain.battery.result import BatteryResult
from domain.exceptions import ConfigValidationError
from domain.product_group_result import TireAndDiskResult
from domain.product_groups import ProductGroup
from domain.row_item.row_item import RowItem
from parsers.battery.grouping import group_batteries
from services.parse_result import ParseResult
from services.parse_statistics import GroupStatistics
from services.vendor_source import VendorSource

if TYPE_CHECKING:
    from services.parse_orchestrator import GrouperFactory


def _doubles_summary(doubles: list[RowItem]) -> str:
    """Строка итога по дублям: всего и сколько из них сомнительных по цене."""
    doubtful = sum(1 for row in doubles if row.duplicate.doubtful_price)
    return f'\nКоличество дублей: {len(doubles)}, из них сомнительных (цена ±5%): {doubtful}\n'


def group_packages(
    parsed: ParseResult, tire_factory: GrouperFactory, source: VendorSource, target: logging.Logger
) -> None:
    """Сохранить связь модели с её группировкой, отклоняя неизвестные пакеты."""
    for group, package in parsed.groups.items():
        if isinstance(package, BatteryResult):
            _group_batteries(parsed, package)
        elif isinstance(package, TireAndDiskResult):
            _group_tires(parsed, tire_factory, source, target)
        else:
            raise ConfigValidationError(f'Группировка группы {group.value} ещё не реализована')


def _group_batteries(parsed: ParseResult, package: BatteryResult) -> None:
    grouped = group_batteries(package)
    parsed.replace_package(grouped)
    parsed.statistics.setdefault(grouped.product_group, GroupStatistics())
    counters = parsed.statistics[grouped.product_group]
    counters.item_count = len(grouped.positions)
    counters.priced_items = sum(row.offer.sale_price is not None for row in grouped.positions)
    counters.doubles = sum(not row.duplicate.is_main for row in grouped.positions)


def _group_tires(
    parsed: ParseResult, tire_factory: GrouperFactory, source: VendorSource, target: logging.Logger
) -> None:
    grouper = tire_factory(
        parsed.tire_and_disk_items, aliases_map=source.aliases_map(), reference_priority=source.reference_priority()
    )
    grouped = grouper.group_by_params().get_row_items()
    parsed.replace_package(TireAndDiskResult(tuple(grouped)))
    counters = parsed.statistics.setdefault(ProductGroup.TIRE_AND_DISK, GroupStatistics())
    counters.item_count = len(grouped)
    counters.priced_items = sum(bool(row.pricing.price_opt) for row in grouped)
    counters.doubles = sum(bool(row.duplicate.is_double) for row in grouped)
    target.info('[%s] %s', ProductGroup.TIRE_AND_DISK.value, _doubles_summary(grouper.get_double_row_items()))
