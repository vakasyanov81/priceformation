"""Формирование прайсов и отчётов из разобранных записей.

Сервис оборачивает ``CommonPriceOut``: пишет прайсы всех активных шаблонов
(или одного выбранного) и отчёт о дублях.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import cast

from domain.row_item.row_item import RowItem
from parsers.common_price_output import CommonPriceOut, WriteDriverFactory, XlsWriterFactory
from services.service_provider import ServiceProvider


class PriceReportService:
    """Формирует прайсы и отчёт о дублях по списку записей."""

    def __init__(self, *, writer_factory: Callable[[list[RowItem]], CommonPriceOut] | None = None) -> None:
        self._writer_factory = writer_factory or common_price_out

    def write_prices(
        self,
        row_items: list[RowItem],
        *,
        template: str | None = None,
        as_jsonl: bool = False,
    ) -> list[str]:
        """Записать прайсы всех активных шаблонов; ``template`` — только выбранный."""
        writer = self._writer_factory(row_items)
        return writer.write_all_prices(result_template=template, as_jsonl=as_jsonl)

    def write_doubles(self, row_items: list[RowItem], *, as_jsonl: bool = False) -> str:
        """Записать отчёт о дублях и вернуть путь файла."""
        return self._writer_factory(row_items).write_doubles_report(as_jsonl=as_jsonl)


def common_price_out(row_items: list[RowItem]) -> CommonPriceOut:
    """CommonPriceOut с фабриками записи из контейнера."""
    return CommonPriceOut(
        row_items,
        xls_writer=cast(XlsWriterFactory, ServiceProvider.resolve(XlsWriterFactory)),
        write_driver=cast(WriteDriverFactory, ServiceProvider.resolve(WriteDriverFactory)),
    )
