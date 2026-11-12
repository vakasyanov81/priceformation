"""Формирование прайсов и отчётов из разобранных записей.

Сервис оборачивает ``CommonPriceOut``: пишет прайсы всех активных шаблонов
(или одного выбранного) и отчёт о дублях.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable

from domain.protocols import ConfigProvider
from domain.row_item.row_item import RowItem
from parsers.common_price.group_output import output_sources, write_group_prices
from parsers.common_price.output import CommonPriceOut
from parsers.writer.factories import WriteDriverFactory, XlsWriterFactory
from parsers.writer.group_files import GroupFileWriter
from services.parse_result import ParseResult

logger = logging.getLogger(__name__)


class PriceReportService:
    """Формирует прайсы и отчёт о дублях по списку записей."""

    def __init__(
        self,
        *,
        writer_factory: Callable[[list[RowItem]], CommonPriceOut],
        group_writer_factory: Callable[[], GroupFileWriter] | None = None,
        config_provider: Callable[[], ConfigProvider] | None = None,
    ) -> None:
        self._writer_factory = writer_factory
        self._group_writer_factory = group_writer_factory
        self._config_provider = config_provider

    @classmethod
    def from_factories(
        cls,
        *,
        xls_writer: XlsWriterFactory,
        write_driver: WriteDriverFactory,
        config_provider: Callable[[], ConfigProvider],
    ) -> PriceReportService:
        """Собрать сервис с готовыми writer-фабриками и динамическими путями окружения."""

        def writer_factory(row_items: list[RowItem]) -> CommonPriceOut:
            return CommonPriceOut(
                row_items,
                xls_writer=xls_writer,
                write_driver=write_driver,
                config_provider=config_provider(),
            )

        def group_writer_factory() -> GroupFileWriter:
            return GroupFileWriter(
                xls_writer=xls_writer, write_driver=write_driver, result_folder=config_provider().result_folder()
            )

        return cls(
            writer_factory=writer_factory, group_writer_factory=group_writer_factory, config_provider=config_provider
        )

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

    def write_result(self, parsed: ParseResult, *, template: str | None = None, as_jsonl: bool = False) -> list[str]:
        """Сохранить границы пакетов от оркестратора до выходных преобразователей."""
        if self._group_writer_factory is None or self._config_provider is None:
            raise RuntimeError('Фабрика групповой записи не настроена')
        start_time = time.monotonic()
        logger.info('Начало формирования и сохранения итоговых прайсов')
        sources = output_sources(parsed.groups, self._config_provider())
        paths = write_group_prices(
            self._group_writer_factory(), sources, template=template, as_jsonl=as_jsonl, selected=parsed.groups.keys()
        )
        elapsed = time.monotonic() - start_time
        logger.info(f'Итоговые прайсы сформированы и сохранены ({elapsed:.2f} сек), файлов: {len(paths)}\n')
        return paths

    def write_doubles(self, row_items: list[RowItem], *, as_jsonl: bool = False) -> str:
        """Записать отчёт о дублях и вернуть путь файла."""
        return self._writer_factory(row_items).write_doubles_report(as_jsonl=as_jsonl)
