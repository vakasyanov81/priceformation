"""Оркестрация отчёта о дублях: разбор прайсов и запись отчёта."""

from __future__ import annotations

from dataclasses import dataclass

from domain.row_item.row_item import RowItem
from services.parse_orchestrator import ParseOrchestrator
from services.parse_result import ParseResult, ParseSelection
from services.price_report import PriceReportService


@dataclass
class DoublesReport:
    """Результат отчёта о дублях: разобранные позиции, найденные дубли и путь файла."""

    parse_result: ParseResult
    doubles: list[RowItem]
    path: str | None


class DoublesService:
    """Парсит прайсы поставщиков и формирует отчёт о дублях."""

    def __init__(
        self,
        *,
        orchestrator: ParseOrchestrator,
        report_service: PriceReportService,
    ) -> None:
        self._orchestrator = orchestrator
        self._report_service = report_service

    def make_report(self, *, as_jsonl: bool = False, selection: ParseSelection | None = None) -> DoublesReport:
        """Разобрать всех поставщиков и записать отчёт о дублях."""
        parse_result = (
            self._orchestrator.parse_all() if selection is None else self._orchestrator.parse_all(selection=selection)
        )
        if not parse_result.groups:
            return DoublesReport(parse_result=parse_result, doubles=[], path=None)
        doubles = [
            row for row in parse_result.tire_and_disk_items if row.duplicate.is_double or row.duplicate.double_candidate
        ]
        path = self._report_service.write_doubles(parse_result.tire_and_disk_items, as_jsonl=as_jsonl)
        return DoublesReport(parse_result=parse_result, doubles=doubles, path=path)
