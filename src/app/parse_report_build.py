"""Сборка полей JSON-отчёта из ParseResult."""

from typing import Any

from app.parse_report import JsonReport, ok_payload
from domain.config_context import get_config_provider
from domain.row_item.row_item import RowItem
from parsers.all_vendors import split_vendor_supplier_info
from parsers.base_parser.parse_statistic import ParseResultStatistic
from services.parse_logging import skips_messages
from services.parse_result import ParseResult


def stats_from_result(parse_result: ParseResult, elapsed: float) -> dict[str, Any]:
    """Счётчики и вилка наценки по результату разбора."""
    statistic = ParseResultStatistic(parse_result.tire_and_disk_items)
    percent = statistic.real_percents_markup()
    absolute = statistic.real_absolute_markup()
    return {
        'items': len(parse_result.tire_and_disk_items),
        'priced_items': statistic.count_items(),
        'doubles': _double_count(parse_result.tire_and_disk_items),
        'unknown_category_skips': len(parse_result.tire_and_disk_diagnostics.unknown_category_skips),
        'black_list_skips': sum(stats.black_list_skips for stats in parse_result.statistics.values()),
        'type_corrections': parse_result.tire_and_disk_diagnostics.type_corrections,
        'title_conflicts': parse_result.tire_and_disk_diagnostics.title_conflicts,
        'elapsed_seconds': round(elapsed, 2),
        'percent_markup': {'min': percent[0], 'max': percent[1]},
        'absolute_markup': {'min': absolute[0], 'max': absolute[1]},
    }


def warnings_from_result(parse_result: ParseResult) -> list[str]:
    """Предупреждения сохраняют контекст группы как в консольной сводке."""
    return [message.strip() for _, message in skips_messages(parse_result)]


def row_items_to_json(rows: list[RowItem]) -> list[dict[str, Any]]:
    """RowItem → словари для JSON."""
    return [_item_payload(row) for row in rows]


def report_from_result(
    action: str,
    parse_result: ParseResult,
    files: list[str],
    elapsed: float,
    rows: list[RowItem] | None = None,
    all_result: bool = False,
) -> JsonReport:
    """Успешный отчёт по уже разобранному результату.
    Без all_result позиции не включаются — только статистика процесса.
    """
    selected = parse_result.tire_and_disk_items if rows is None else rows
    positions = row_items_to_json(selected) if all_result else []
    enabled, disabled = split_vendor_supplier_info(get_config_provider())
    payload = ok_payload(
        action=action,
        positions=positions,
        stats=stats_from_result(parse_result, elapsed),
        warnings=warnings_from_result(parse_result),
        files=files,
        suppliers=enabled,
    )
    payload['disabled_suppliers'] = disabled
    return payload


def _item_payload(row: RowItem) -> dict[str, Any]:
    payload = row.to_dict()
    if row.parse_errors:
        payload['parse_errors'] = row.parse_errors
    return payload


def _double_count(rows: list[RowItem]) -> int:
    return sum(1 for row in rows if row.duplicate.is_double or row.duplicate.double_candidate)
