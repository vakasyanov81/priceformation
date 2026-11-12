"""Запись XLSX-книг из пакетов групп после общей проверки."""

from collections.abc import Mapping, Sequence, Set
from pathlib import Path

from domain.product_groups import ProductGroup
from parsers.writer.factories import WriteDriverFactory, XlsWriterFactory
from parsers.writer.jsonl_writer import write_plan_jsonl
from parsers.writer.output_plan import GroupOutputSource, WorkbookPlan, prepare_output_plan
from parsers.writer.templates.group_output import TemplateOutput
from parsers.writer.templates.sheet_template import SheetTemplate


class GroupFileWriter:
    """Каждая книга получает собственный драйвер, колонки и оформление."""

    def __init__(self, *, xls_writer: XlsWriterFactory, write_driver: WriteDriverFactory, result_folder: str) -> None:
        self._xls_writer = xls_writer
        self._write_driver = write_driver
        self._result_folder = result_folder

    def write(
        self,
        outputs: Sequence[TemplateOutput],
        sources: Mapping[ProductGroup, GroupOutputSource],
        *,
        selected: Set[ProductGroup] | None = None,
        current_date: str | None = None,
        as_jsonl: bool = False,
    ) -> list[str]:
        """Подготовить весь план до создания драйверов и файлов."""
        books = prepare_output_plan(outputs, sources, selected=selected, current_date=current_date)
        return self.write_plan(books, as_jsonl=as_jsonl)

    def write_plan(self, books: tuple[WorkbookPlan, ...], *, as_jsonl: bool = False) -> list[str]:
        """Записать полностью подготовленный план после проверки всех преобразователей."""
        if as_jsonl:
            return write_plan_jsonl(books, self._result_folder)
        return [self._write_book(book) for book in books]

    def _write_book(self, book: WorkbookPlan) -> str:
        driver = self._write_driver()
        multiple_sheets = len(book.sheets) > 1
        if multiple_sheets:
            Path(self._result_folder).mkdir(parents=True, exist_ok=True)
            driver.init_workbook(self._result_folder, book.file_name)
        result_path = ''
        for sheet in book.sheets:
            writer = self._xls_writer(
                driver,
                [dict(row) for row in sheet.rows],
                SheetTemplate(book.file_name, sheet.settings),
                result_folder=self._result_folder,
            )
            if multiple_sheets:
                writer.write_sheet()
            else:
                writer.write()
            result_path = writer.get_result_path()
        if multiple_sheets:
            driver.save()
        return result_path
