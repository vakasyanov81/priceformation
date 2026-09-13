"""Оркестрация отчёта о дублях: разбор прайсов и запись отчёта."""

from __future__ import annotations

from dataclasses import dataclass

from parsers.row_item.row_item import RowItem
from services.parse_orchestrator import ParseOrchestrator, ParseResult
from services.price_report import PriceReportService


@dataclass
class DoublesReport:
    """Результат отчёта о дублях: разобранные позиции, найденные дубли и путь файла."""

    parse_result: ParseResult
    doubles: list[RowItem]
    path: str


class DoublesService:
    """Парсит прайсы поставщиков и формирует отчёт о дублях."""

    def __init__(
        self,
        *,
        orchestrator: ParseOrchestrator | None = None,
        report_service: PriceReportService | None = None,
    ) -> None:
        self._orchestrator = orchestrator or ParseOrchestrator()
        self._report_service = report_service or PriceReportService()

    def make_report(self, *, as_jsonl: bool = False) -> DoublesReport:
        """Разобрать всех поставщиков и записать отчёт о дублях."""
        parse_result = self._orchestrator.parse_all()
        doubles = [row for row in parse_result.parsed_items if row.is_double or row.double_candidate]
        path = self._report_service.write_doubles(parse_result.parsed_items, as_jsonl=as_jsonl)
        return DoublesReport(parse_result=parse_result, doubles=doubles, path=path)
