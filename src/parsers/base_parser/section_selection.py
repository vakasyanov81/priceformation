"""Состояние разделов исходного листа до strip, отображения и разбора товаров."""

from collections.abc import Iterator

from parsers.base_parser.routing_rows import RouteSection
from parsers.raw_table import RawRow, RawTable
from parsers.vendor_config.section_selector import SectionSelector

type CandidateRow = tuple[RawRow, list[RouteSection]]


class SectionSelection:
    """Запоминает корневой раздел; вложенные заголовки не меняют выбор."""

    def __init__(self, selector: SectionSelector | None) -> None:
        self._selector = selector
        self._selected = False

    def accepts(self, row: RawRow) -> bool:
        """Заголовок содержит только название, товар — также данные других колонок."""
        selector = self._selector
        if selector is None:
            return True
        title = row.fields.get(selector.column)
        if not isinstance(title, str) or not title.strip():
            return False
        other_fields = dict(row.fields)
        other_fields.pop(selector.column, None)
        if any(cell not in ('', None) for cell in other_fields.values()):
            return self._selected
        if title == title.lstrip():
            self._selected = selector.matches(title)
        return False


def section_candidates(table: RawTable, sections: list[RouteSection]) -> Iterator[CandidateRow]:
    """Читать заголовки до start_row; состояние изолировано для каждого листа."""
    selections = [SectionSelection(section.section_selector) for section in sections]
    start_row = sections[0].start_row
    for row in table.rows:
        selected = _selected_sections(row, sections, selections)
        has_data = any(row.fields.values())
        if row.row_number >= start_row and has_data:
            yield row, selected


def _selected_sections(
    row: RawRow, sections: list[RouteSection], selections: list[SectionSelection]
) -> list[RouteSection]:
    selected = []
    for section, selection in zip(sections, selections, strict=True):
        if selection.accepts(row):
            selected.append(section)
    return selected
