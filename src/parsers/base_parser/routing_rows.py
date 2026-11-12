"""Операции маршрутизации и отображения отдельных исходных строк."""

import logging

from domain.exceptions import CoreExceptionError
from parsers.base_parser.base_parser_config import ParserParams
from parsers.raw_table import RawRow, RawTable
from parsers.vendor_config.group_models import BatterySection
from parsers.vendor_config.models import READER_JSON, VendorConfig
from parsers.vendor_config.section_models import VendorSection
from parsers.xls_reader_row import strip_cell_value

logger = logging.getLogger(__name__)

type RouteSection = VendorSection | BatterySection
type RawFields = dict[str, object]


class RowRoutingError(CoreExceptionError):
    """Строка прайса имеет несколько допустимых маршрутов."""


def selects_table(section: RouteSection, table: RawTable) -> bool:
    return table.sheet_index is None or not section.sheet_indexes or table.sheet_index in section.sheet_indexes


def matches(section: RouteSection, row: RawRow) -> bool:
    return section.row_selector is None or section.row_selector.matches(row.fields)


def raise_ambiguous(
    config: VendorConfig,
    path: str,
    table: RawTable,
    row: RawRow,
    sections: list[RouteSection],
) -> None:
    routes = ', '.join(f'{section.id} ({section.product_group})' for section in sections)
    sheet = 'JSON' if table.sheet_index is None else str(table.sheet_index)
    location = f'Поставщик {config.folder}, файл {path}'
    row_location = f'лист {sheet}, строка {row.row_number}'
    raise RowRoutingError(f'{location}, {row_location}: неоднозначная маршрутизация — {routes}')


def log_unrouted(config: VendorConfig, path: str, table: RawTable, unrouted: int) -> None:
    sheet = 'JSON' if table.sheet_index is None else str(table.sheet_index + 1)
    logger.warning(
        '%s: файл %s, лист %s: пропущено строк — %d (не подходят под настройки отбора разделов или товаров)',
        config.name,
        path,
        sheet,
        unrouted,
    )


def map_row(config: VendorConfig, row: RawRow, section_params: ParserParams) -> RawFields:
    mapped: RawFields = {}
    for source, target in section_params.columns.items():
        key = str(source)
        if config.reader == READER_JSON and key not in row.fields:
            continue
        cell = row.fields[key]
        if config.reader == READER_JSON:
            mapped[str(target)] = cell
        else:
            mapped[str(target)] = strip_cell_value(cell)
    return mapped
