"""Фабрики драйвера и XLSX-писателя для внедрения при композиции."""

from typing import Protocol

from parsers.writer.ixlsx_driver import IXlsDriver
from parsers.writer.row_style import PriceRow
from parsers.writer.templates.iwrite_template import IWriteTemplate
from parsers.writer.xls_writer import XlsWriter


class WriteDriverFactory(Protocol):
    """Фабрика независимого драйвера для каждой книги."""

    def __call__(self) -> IXlsDriver: ...


class XlsWriterFactory(Protocol):
    """Писатель принимает класс старого шаблона или готовое описание листа."""

    def __call__(
        self,
        driver: IXlsDriver,
        parse_result: list[PriceRow],
        template: type[IWriteTemplate] | IWriteTemplate,
        *,
        result_folder: str,
    ) -> XlsWriter: ...
