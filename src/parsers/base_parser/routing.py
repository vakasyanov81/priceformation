"""Совместная маршрутизация файлов, листов и исходных строк всех секций поставщика."""

from collections import defaultdict
from collections.abc import Iterator
from pathlib import Path

from domain.exceptions import SupplierNotHavePricesError
from parsers.base_parser.base_parser_config import ParseParamsSupplier, ParserParams
from parsers.base_parser.protocols import FileReaderProtocol
from parsers.base_parser.routing_rows import (
    log_unrouted,
    map_row,
    matches,
    raise_ambiguous,
    selects_table,
)
from parsers.base_parser.routing_validation import ensure_sheet_indexes, validate_table
from parsers.raw_table import RawRow, RawTable
from parsers.vendor_config.group_models import BatterySection
from parsers.vendor_config.models import VendorConfig
from parsers.vendor_config.section_models import VendorSection

type RouteSection = VendorSection | BatterySection
type SectionRows = dict[str, list[RawRow]]
type FilePaths = list[str]


class VendorRouting:
    """Общие маршруты поставщика; выбор одной секции не скрывает неоднозначность остальных."""

    def __init__(self, config: VendorConfig) -> None:
        self._config = config
        self._sections = tuple(section for group in config.product_groups for section in group.sections)
        self._section_params = {section.id: self._params_for(section) for section in self._sections}
        self._reader: FileReaderProtocol | None = None
        self._paths: dict[str, str] = {}
        self._path_sections: dict[str, list[RouteSection]] = defaultdict(list)
        self._section_paths: dict[str, list[str]] = defaultdict(list)
        self._section_rows: SectionRows = defaultdict(list)
        self._resolved = False
        self._routed = False
        self._unrouted_rows = 0

    @property
    def unrouted_rows(self) -> int:
        return self._unrouted_rows

    def resolve(
        self,
        section_id: str,
        reader: FileReaderProtocol,
        given_files: FilePaths | None = None,
    ) -> list[str]:
        """Разрешить пути всех секций, устраняя повторы после канонизации пути."""
        if not self._resolved:
            self._reader = reader
            for section in self._sections:
                paths = given_files or reader.price_files(self._section_params[section.id])
                self._remember_paths(section, paths)
            self._resolved = True
        files = self._section_paths[section_id]
        if not files:
            supplier_name = self._section_params[section_id].supplier.name
            raise SupplierNotHavePricesError(f'Прайсов у поставщика ({supplier_name}) не обнаружено!')
        return files

    def read_rows(self, section_id: str) -> list[dict[str, object]]:
        """Завершить маршрутизацию всех таблиц до отображения строк выбранной секции."""
        if not self._routed:
            self._route_all()
        section_params = self._section_params[section_id]
        source_rows = self._section_rows[section_id]
        return [map_row(self._config, row, section_params) for row in source_rows]

    def _params_for(self, section: RouteSection) -> ParserParams:
        return ParserParams(
            supplier=ParseParamsSupplier(folder_name=self._config.folder, name=section.name, code=section.id),
            start_row=section.start_row,
            sheet_info=section.sheet_info,
            columns=dict(section.columns) if isinstance(section, VendorSection) else {},
            stop_words=(),
            file_templates=section.file_templates,
            sheet_indexes=section.sheet_indexes,
        )

    def _remember_paths(self, section: RouteSection, paths: list[str]) -> None:
        for path in paths:
            canonical = str(Path(path).resolve())
            self._paths.setdefault(canonical, path)
            if section not in self._path_sections[canonical]:
                self._path_sections[canonical].append(section)
            if self._paths[canonical] not in self._section_paths[section.id]:
                self._section_paths[section.id].append(self._paths[canonical])

    def _route_all(self) -> None:
        reader = self._reader
        if reader is None:
            raise RuntimeError('Файлы поставщика не разрешены перед маршрутизацией')
        self._unrouted_rows = sum(
            _route_file(self._config, reader, self._paths[canonical], sections, self._section_rows)
            for canonical, sections in self._path_sections.items()
        )
        self._routed = True


def _route_file(
    config: VendorConfig,
    reader: FileReaderProtocol,
    path: str,
    sections: list[RouteSection],
    section_rows: SectionRows,
) -> int:
    sheet_indexes = tuple(sorted({index for section in sections for index in section.sheet_indexes}))
    tables = reader.raw_tables(path, sheet_indexes)
    ensure_sheet_indexes(path, sections, tables)
    return sum(_route_table(config, path, sections, table, section_rows) for table in tables)


def _route_table(
    config: VendorConfig,
    path: str,
    file_sections: list[RouteSection],
    table: RawTable,
    section_rows: SectionRows,
) -> int:
    sections = [section for section in file_sections if selects_table(section, table)]
    if not sections:
        return 0
    validate_table(path, table, sections)
    data_rows = _data_rows(table, sections[0].start_row)
    unrouted = 0
    for row in data_rows:
        if not _assign_row(config, path, table, row, sections, section_rows):
            unrouted += 1
    if unrouted:
        log_unrouted(config, path, table, unrouted)
    return unrouted


def _data_rows(table: RawTable, start_row: int) -> Iterator[RawRow]:
    for row in table.rows:
        if row.row_number < start_row:
            continue
        if any(row.fields.values()):
            yield row


def _assign_row(
    config: VendorConfig,
    path: str,
    table: RawTable,
    row: RawRow,
    sections: list[RouteSection],
    section_rows: SectionRows,
) -> bool:
    matched = [section for section in sections if matches(section, row)]
    if len(matched) > 1:
        raise_ambiguous(config, path, table, row, matched)
    if not matched:
        return False
    section_rows[matched[0].id].append(row)
    return True
