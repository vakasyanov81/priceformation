"""Сборка полей JSON-отчёта из ParseResult."""

from typing import Any

from app.parse_report import ok_payload
from app.parse_report_groups import groups_from_result, positions_to_json
from app.parse_report_types import JsonReport
from domain.config_context import get_config_provider
from domain.product_group_result import TireAndDiskResult
from domain.row_item.row_item import RowItem
from parsers.all_vendors import split_vendor_supplier_info
from services.parse_logging import skips_messages
from services.parse_result import ParseResult


def stats_from_result(parse_result: ParseResult, elapsed: float) -> dict[str, Any]:
    """Счётчики и вилка наценки по результату разбора."""
    totals = parse_result.total_statistics()
    return {
        'items': totals.item_count,
        'priced_items': totals.priced_items,
        'doubles': totals.doubles,
        'black_list_skips': totals.black_list_skips,
        'unrouted_rows': parse_result.unrouted_rows,
        'elapsed_seconds': round(elapsed, 2),
    }


def warnings_from_result(parse_result: ParseResult) -> list[str]:
    """Предупреждения сохраняют контекст группы как в консольной сводке."""
    return [message.strip() for _, message in skips_messages(parse_result)]


def row_items_to_json(rows: list[RowItem]) -> list[dict[str, Any]]:
    """RowItem → словари для JSON."""
    return positions_to_json(TireAndDiskResult(tuple(rows)))


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
    enabled, disabled = split_vendor_supplier_info(get_config_provider())
    payload = ok_payload(
        action=action,
        groups=groups_from_result(parse_result, all_result=all_result, rows=rows),
        stats=stats_from_result(parse_result, elapsed),
        warnings=warnings_from_result(parse_result),
        files=files,
        suppliers=enabled,
    )
    payload['disabled_suppliers'] = disabled
    return payload
