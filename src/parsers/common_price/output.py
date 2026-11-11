"""
Make parse all price and make inner and drom prices
"""

from datetime import date
from pathlib import Path
from typing import Any

from domain.product_group_result import TireAndDiskResult
from domain.product_groups import ProductGroup
from domain.protocols import ConfigProvider
from domain.row_item.row_item import RowItem
from parsers.base_parser.nomenclature_correction import (
    clear_nomenclature_cache,
    get_nomenclature_corrected_title,
)
from parsers.common_price.doubles_order import priority_first
from parsers.common_price.tire_output import TireOutputSource
from parsers.data_provider.doubles_settings import DoublesSettings, load_doubles_settings
from parsers.writer.factories import WriteDriverFactory, XlsWriterFactory
from parsers.writer.group_files import GroupFileWriter
from parsers.writer.jsonl_writer import RESULT_META_FILE, write_template_jsonl
from parsers.writer.output_validation import validate_outputs
from parsers.writer.templates.all_templates import (
    all_writer_templates,
    get_writer_template,
    writer_templates_by_name,
)
from parsers.writer.templates.iwrite_template import IWriteTemplate
from parsers.writer.templates.tmpl.for_doubles import ForDoubles


class CommonPriceOut:
    """
    Make parse all price and make inner and drom prices
    """

    def __init__(
        self,
        row_items: list[RowItem],
        *,
        xls_writer: XlsWriterFactory,
        write_driver: WriteDriverFactory,
        config_provider: ConfigProvider,
        doubles_settings: DoublesSettings | None = None,
    ) -> None:
        """init"""
        self.xls_writer = xls_writer
        self.write_driver = write_driver
        self.row_items = row_items
        self._config_provider = config_provider
        self._doubles_settings = doubles_settings

    def nomenclature_title_correction(self) -> None:
        """make correct nomenclature title"""
        for row_item in self.row_items:
            title = row_item.identity.title
            if title is None:
                continue
            row_item.set_field('title', get_nomenclature_corrected_title(title, self._config_provider))

    def write_all_prices(
        self,
        *,
        as_jsonl: bool = False,
        result_template: str | None = None,
    ) -> list[str]:
        """
        Make prices for all active templates and the duplicates report.
        :return: пути записанных файлов
        """
        templates = _templates_to_write(result_template)
        current_date = date.today().isoformat()
        validate_outputs(
            [template().output_spec() for template in (*templates, ForDoubles)],
            {ProductGroup.TIRE_AND_DISK},
            current_date=current_date,
        )
        doubles_settings = self._settings()
        clear_nomenclature_cache()
        self.nomenclature_title_correction()
        written = [
            self._write_with_template(
                self._rows_for(write_template, doubles_settings) if as_jsonl else self.row_items,
                write_template,
                as_jsonl=as_jsonl,
                current_date=current_date,
            )
            for write_template in templates
        ]
        written.append(self.write_doubles_report(as_jsonl=as_jsonl, current_date=current_date))
        if as_jsonl:
            return jsonl_output_files(written)
        return written

    def write_doubles_report(self, *, as_jsonl: bool = False, current_date: str | None = None) -> str:
        """Write only items marked as duplicates and return the file path."""
        doubles = [
            row_item
            for row_item in self.row_items
            if row_item.duplicate.is_double or row_item.duplicate.double_candidate
        ]
        return self._write_with_template(
            priority_first(doubles, self._settings().priority_suppliers),
            ForDoubles,
            as_jsonl=as_jsonl,
            current_date=current_date,
        )

    def _settings(self) -> DoublesSettings:
        """Настройки дублей: переданные в конструктор или из parse_config/doubles.json."""
        if self._doubles_settings is None:
            self._doubles_settings = load_doubles_settings(tuple(writer_templates_by_name()), self._config_provider)
        return self._doubles_settings

    def _rows_for(self, template: type[IWriteTemplate], doubles_settings: DoublesSettings) -> list[RowItem]:
        """Строки под шаблон: склады одной группы сводятся в строку, дубли исключаются по настройке.

        Сначала склады, потом дубли: сравниваются уже сведённые строки поставщиков.
        """
        source = TireOutputSource(TireAndDiskResult(tuple(self.row_items)), doubles_settings)
        return source.positions_for(template.template_id, template().output_spec().groups[0])

    def _write_with_template(
        self,
        rows: list[RowItem],
        template: type[IWriteTemplate],
        *,
        as_jsonl: bool = False,
        current_date: str | None = None,
    ) -> str:
        """Записать файл шаблона (xlsx или jsonl) и вернуть путь."""
        folder = self._config_provider.result_folder()
        if as_jsonl:
            validate_outputs([template().output_spec()], {ProductGroup.TIRE_AND_DISK}, current_date=current_date)
            return write_template_jsonl(_to_raw_dicts(rows), template, folder)
        writer = GroupFileWriter(
            xls_writer=self.xls_writer,
            write_driver=self.write_driver,
            result_folder=folder,
        )
        source = TireOutputSource(TireAndDiskResult(tuple(rows)), self._settings())
        return writer.write(
            [template().output_spec()], {ProductGroup.TIRE_AND_DISK: source}, current_date=current_date
        )[0]


def jsonl_output_files(written: list[str]) -> list[str]:
    """Пути jsonl и файл метаинформации колонок в той же папке."""
    if not written:
        return written
    meta = str(Path(written[0]).parent / RESULT_META_FILE)
    if meta in written:
        return written
    return [*written, meta]


def _templates_to_write(result_template: str | None) -> list[type[IWriteTemplate]]:
    """Все активные шаблоны или один выбранный по имени CLI."""
    if result_template is None:
        return all_writer_templates()
    return [get_writer_template(result_template)]


def _to_raw_dicts(row_items: list[RowItem]) -> list[dict[str, Any]]:
    """RowItem → dict для шаблонов записи."""
    return [row_item.to_dict() for row_item in row_items]
