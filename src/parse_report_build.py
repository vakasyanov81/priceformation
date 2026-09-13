"""Сборка полей JSON-отчёта из ParseResult."""

from typing import Any

from parse_report import JsonReport, ok_payload
from parsers.all_vendors import split_vendor_supplier_info
from parsers.base_parser.category_finder import skipped_unknown_categories_message
from parsers.base_parser.parse_statistic import ParseResultStatistic
from parsers.data_provider.black_list import skipped_black_list_message
from parsers.row_item.row_item import RowItem
from services.parse_orchestrator import ParseResult


def stats_from_result(parse_result: ParseResult, elapsed: float) -> dict[str, Any]:
    """Счётчики и вилка наценки по результату разбора."""
    statistic = ParseResultStatistic(parse_result.parsed_items)
    percent = statistic.real_percents_markup()
    absolute = statistic.real_absolute_markup()
    return {
        'items': len(parse_result.parsed_items),
        'priced_items': statistic.count_items(),
        'doubles': _double_count(parse_result.parsed_items),
        'unknown_category_skips': len(parse_result.unknown_category_skips),
        'black_list_skips': parse_result.black_list_skips,
        'elapsed_seconds': round(elapsed, 2),
        'percent_markup': {'min': percent[0], 'max': percent[1]},
        'absolute_markup': {'min': absolute[0], 'max': absolute[1]},
    }


def warnings_from_result(parse_result: ParseResult) -> list[str]:
    """Тексты предупреждений разбора (категории, black_list)."""
    collected: list[str] = []
    category = skipped_unknown_categories_message(parse_result.unknown_category_skips)
    if category:
        collected.append(category.strip())
    black_list = skipped_black_list_message(parse_result.black_list_skips)
    if black_list:
        collected.append(black_list.strip())
    return collected


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
    selected = parse_result.parsed_items if rows is None else rows
    positions = row_items_to_json(selected) if all_result else []
    enabled, disabled = split_vendor_supplier_info()
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
    return sum(1 for row in rows if row.is_double or row.double_candidate)
