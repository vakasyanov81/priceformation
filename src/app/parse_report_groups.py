"""Сериализация пакетов и статистики с сохранением границ моделей."""

from functools import singledispatch
from typing import Any

from app.parse_report_types import JsonGroup
from domain.product_group_result import TireAndDiskResult
from domain.product_groups import ProductGroup
from domain.row_item.row_item import RowItem
from parsers.base_parser.parse_statistic import ParseResultStatistic
from services.parse_result import ParseResult
from services.parse_statistics import GroupStatistics


@singledispatch
def positions_to_json(package: object) -> list[dict[str, Any]]:
    """Преобразователь определяется моделью пакета, а не набором полей строки."""
    raise TypeError(f'Нет JSON-преобразователя для пакета {type(package).__name__}')


@positions_to_json.register
def _tire_positions(package: TireAndDiskResult) -> list[dict[str, Any]]:
    positions = []
    for row in package.positions:
        payload = row.to_dict()
        if row.parse_errors:
            payload['parse_errors'] = row.parse_errors
        positions.append(payload)
    return positions


def groups_from_result(
    parsed: ParseResult,
    *,
    all_result: bool,
    rows: list[RowItem] | None = None,
) -> dict[str, JsonGroup]:
    """Сохранить выбранные пустые пакеты и полную статистику при фильтрации дублей."""
    groups: dict[str, JsonGroup] = {}
    for group, package in parsed.groups.items():
        selected = package
        if group is ProductGroup.TIRE_AND_DISK and rows is not None:
            selected = TireAndDiskResult(tuple(rows))
        stats = _common_statistics(parsed, group)
        if group is ProductGroup.TIRE_AND_DISK:
            stats.update(_tire_statistics(parsed))
        groups[group.value] = {
            'positions': positions_to_json(selected) if all_result else [],
            'stats': stats,
        }
    return groups


def _common_statistics(parsed: ParseResult, group: ProductGroup) -> dict[str, Any]:
    counters = parsed.statistics.get(group, GroupStatistics())
    return {
        'items': len(parsed.groups[group].positions),
        'priced_items': counters.priced_items,
        'doubles': counters.doubles,
        'black_list_skips': counters.black_list_skips,
    }


def _tire_statistics(parsed: ParseResult) -> dict[str, Any]:
    statistic = ParseResultStatistic(parsed.tire_and_disk_items)
    percent = statistic.real_percents_markup()
    absolute = statistic.real_absolute_markup()
    diagnostics = parsed.tire_and_disk_diagnostics
    return {
        'unknown_category_skips': len(diagnostics.unknown_category_skips),
        'type_corrections': diagnostics.type_corrections,
        'title_conflicts': diagnostics.title_conflicts,
        'percent_markup': {'min': percent[0], 'max': percent[1]},
        'absolute_markup': {'min': absolute[0], 'max': absolute[1]},
    }
