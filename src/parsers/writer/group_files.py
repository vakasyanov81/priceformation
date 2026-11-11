"""Запись отдельных XLSX-книг из пакетов групп после общей проверки."""

from collections.abc import Mapping, Sequence, Set

from domain.exceptions import ConfigValidationError
from domain.product_groups import ProductGroup
from parsers.writer.factories import WriteDriverFactory, XlsWriterFactory
from parsers.writer.output_plan import GroupOutputSource, WorkbookPlan, prepare_output_plan
from parsers.writer.templates.group_output import OutputMode, TemplateOutput
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
    ) -> list[str]:
        """Подготовить весь план до создания драйверов и файлов."""
        if any(output.mode != OutputMode.SEPARATE_FILES for output in outputs):
            raise ConfigValidationError('Запись workbook_sheets ещё недоступна; используйте separate_files')
        books = prepare_output_plan(outputs, sources, selected=selected, current_date=current_date)
        return [self._write_book(book) for book in books]

    def _write_book(self, book: WorkbookPlan) -> str:
        sheet = book.sheets[0]
        writer = self._xls_writer(
            self._write_driver(),
            [dict(row) for row in sheet.rows],
            SheetTemplate(book.file_name, sheet.settings),
            result_folder=self._result_folder,
        )
        writer.write()
        return writer.get_result_path()
