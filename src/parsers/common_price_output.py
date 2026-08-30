"""
Make parse all price and make inner and drom prices
"""

from typing import Any

from core.parse_paths import get_parse_paths
from parsers.base_parser.nomenclature_correction import (
    clear_nomenclature_cache,
    get_nomenclature_corrected_title,
)
from parsers.row_item.row_item import RowItem
from parsers.writer.jsonl_writer import write_template_jsonl
from parsers.writer.templates.all_templates import all_writer_templates
from parsers.writer.templates.iwrite_template import IWriteTemplate
from parsers.writer.templates.tmpl.for_doubles import ForDoubles
from parsers.writer.xls_writer import XlsWriter
from parsers.writer.xwlt_driver import XlsxWriterDriver


class CommonPriceOut:
    """
    Make parse all price and make inner and drom prices
    """

    def __init__(
        self,
        row_items: list[RowItem],
        xls_writer: type[XlsWriter] = XlsWriter,
        write_driver: type[XlsxWriterDriver] = XlsxWriterDriver,
    ) -> None:
        """init"""
        self.xls_writer = xls_writer
        self.write_driver = write_driver
        self.row_items = row_items

    def nomenclature_title_correction(self) -> None:
        """make correct nomenclature title"""
        for row_item in self.row_items:
            row_item.title = get_nomenclature_corrected_title(row_item.title)

    def write_all_prices(self, *, as_jsonl: bool = False) -> list[str]:
        """
        Make prices for all active templates.
        :return: пути записанных файлов
        """
        clear_nomenclature_cache()
        self.nomenclature_title_correction()
        return [
            self._write_with_template(self.row_items, write_template, as_jsonl=as_jsonl)
            for write_template in all_writer_templates()
        ]

    def write_doubles_report(self, *, as_jsonl: bool = False) -> str:
        """Write only items marked as duplicates and return the file path."""
        doubles = [row_item for row_item in self.row_items if row_item.is_double or row_item.double_candidate]
        return self._write_with_template(doubles, ForDoubles, as_jsonl=as_jsonl)

    def _write_with_template(
        self,
        rows: list[RowItem],
        template: type[IWriteTemplate],
        *,
        as_jsonl: bool = False,
    ) -> str:
        """Записать файл шаблона (xlsx или jsonl) и вернуть путь."""
        raw_rows = _to_raw_dicts(rows)
        folder = get_parse_paths().result_folder
        if as_jsonl:
            return write_template_jsonl(raw_rows, template, folder)
        writer = self.xls_writer(
            self.write_driver(),
            raw_rows,
            template,
            result_folder=folder,
        )
        writer.write()
        return writer.get_result_path()


def _to_raw_dicts(row_items: list[RowItem]) -> list[dict[str, Any]]:
    """RowItem → dict для шаблонов записи."""
    return [row_item.to_dict() for row_item in row_items]
