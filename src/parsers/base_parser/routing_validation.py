"""Проверки совместного использования одного физического листа секциями."""

from itertools import combinations

from domain.exceptions import ConfigValidationError
from parsers.raw_table import RawTable
from parsers.vendor_config.group_models import BatterySection
from parsers.vendor_config.section_models import VendorSection

type RouteSection = VendorSection | BatterySection


def ensure_sheet_indexes(path: str, sections: list[RouteSection], tables: list[RawTable]) -> None:
    available = {table.sheet_index for table in tables if table.sheet_index is not None}
    for section in sections:
        missing = set(section.sheet_indexes) - available
        if missing:
            raise ConfigValidationError(
                f'{section.config_path} → sheet_indexes: файл {path}, листы {sorted(missing)} отсутствуют'
            )


def validate_table(path: str, table: RawTable, sections: list[RouteSection]) -> None:
    _validate_start_row(path, table, sections)
    _validate_required_selectors(path, table, sections)
    _validate_selector_overlaps(sections)


def _validate_start_row(path: str, table: RawTable, sections: list[RouteSection]) -> None:
    first = sections[0]
    other_sections = sections[1:]
    different = [section for section in other_sections if section.start_row != first.start_row]
    if not different:
        return
    second = different[0]
    raise ConfigValidationError(
        f'Общий лист {path}, {table.sheet_index}: разные start_row; '
        f'{first.config_path} → start_row и {second.config_path} → start_row'
    )


def _validate_required_selectors(path: str, table: RawTable, sections: list[RouteSection]) -> None:
    missing = [section for section in sections if not _has_selector(section)]
    if len(sections) > 1 and missing:
        raise ConfigValidationError(
            f'Общий лист {path}, {table.sheet_index}: каждая секция должна задать row_selector или section_selector; '
            + ', '.join(section.config_path for section in sections)
        )


def _validate_selector_overlaps(sections: list[RouteSection]) -> None:
    for first, second in combinations(sections, 2):
        common = _selector_overlap(first, second)
        if common:
            raise ConfigValidationError(
                f'Селекторы секций {first.id} и {second.id} пересекаются на значениях {sorted(common)}: '
                f'{first.config_path} → row_selector; {second.config_path} → row_selector'
            )


def _selector_overlap(first: RouteSection, second: RouteSection) -> set[str]:
    if first.row_selector is None or second.row_selector is None:
        return set()
    first_selector = first.row_selector
    second_selector = second.row_selector
    if first_selector.column != second_selector.column:
        return set()
    return set(first_selector.accepted_values) & set(second_selector.accepted_values)


def _has_selector(section: RouteSection) -> bool:
    return section.row_selector is not None or section.section_selector is not None
