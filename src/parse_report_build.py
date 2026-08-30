"""Сборка полей JSON-отчёта из CommonPrice."""

from typing import Any

from parse_report import JsonReport, ok_payload
from parsers.base_parser.category_finder import skipped_unknown_categories_message
from parsers.base_parser.parse_statistic import ParseResultStatistic
from parsers.common_price import CommonPrice
from parsers.data_provider.black_list import skipped_black_list_message
from parsers.row_item.row_item import RowItem


def stats_from_common(common: CommonPrice, elapsed: float) -> dict[str, Any]:
    """Счётчики и вилка наценки по результату разбора."""
    statistic = ParseResultStatistic(common.parsed_items)
    percent = statistic.real_percents_markup()
    absolute = statistic.real_absolute_markup()
    return {
        "items": len(common.parsed_items),
        "priced_items": statistic.count_items(),
        "doubles": _double_count(common.parsed_items),
        "unknown_category_skips": len(common.unknown_category_skips),
        "black_list_skips": common.black_list_skips,
        "elapsed_seconds": round(elapsed, 2),
        "percent_markup": {"min": percent[0], "max": percent[1]},
        "absolute_markup": {"min": absolute[0], "max": absolute[1]},
    }


def warnings_from_common(common: CommonPrice) -> list[str]:
    """Тексты предупреждений разбора (категории, black_list)."""
    collected: list[str] = []
    category = skipped_unknown_categories_message(common.unknown_category_skips)
    if category:
        collected.append(category.strip())
    black_list = skipped_black_list_message(common.black_list_skips)
    if black_list:
        collected.append(black_list.strip())
    return collected


def row_items_to_json(rows: list[RowItem]) -> list[dict[str, Any]]:
    """RowItem → словари для JSON."""
    return [_item_payload(row) for row in rows]


def report_from_common(
    action: str,
    common: CommonPrice,
    files: list[str],
    elapsed: float,
    rows: list[RowItem] | None = None,
    all_result: bool = False,
) -> JsonReport:
    """Успешный отчёт по уже разобранному CommonPrice.
    Без all_result позиции не включаются — только статистика процесса.
    """
    selected = common.parsed_items if rows is None else rows
    positions = row_items_to_json(selected) if all_result else []
    payload = ok_payload(
        action=action,
        positions=positions,
        stats=stats_from_common(common, elapsed),
        warnings=warnings_from_common(common),
        files=files,
        suppliers=common.supplier_info(),
    )
    payload["took"] = f"{round(elapsed)} seconds"
    return payload


def _item_payload(row: RowItem) -> dict[str, Any]:
    payload = row.to_dict()
    if row.parse_errors:
        payload["parse_errors"] = row.parse_errors
    return payload


def _double_count(rows: list[RowItem]) -> int:
    return sum(1 for row in rows if row.is_double or row.double_candidate)
