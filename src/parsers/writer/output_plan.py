"""Подготовка книг и листов без файлового ввода-вывода."""

from collections.abc import Mapping, Sequence, Set
from copy import deepcopy
from dataclasses import dataclass
from datetime import date
from typing import Protocol

from domain.product_group_handler import OutputFields
from domain.product_groups import ProductGroup
from parsers.writer.output_names import output_file_name
from parsers.writer.output_validation import validate_outputs
from parsers.writer.templates.group_output import GroupOutput, OutputMode, TemplateOutput


class GroupOutputSource(Protocol):
    """Связанный с пакетом преобразователь; модель скрыта внутри реализации группы."""

    @property
    def fields(self) -> Set[str]: ...

    @property
    def title_fields(self) -> frozenset[str]: ...

    def prepare(self, template_id: str, settings: GroupOutput) -> tuple[OutputFields, ...]:
        """Применить правила к позициям своей модели, затем сериализовать."""
        ...


@dataclass(frozen=True)
class SheetPlan:
    """Настройки и готовые выходные поля одного листа."""

    settings: GroupOutput
    rows: tuple[OutputFields, ...]
    title_fields: frozenset[str] = frozenset()


@dataclass(frozen=True)
class WorkbookPlan:
    """Одна книга с независимыми листами в порядке шаблона."""

    template_id: str
    file_name: str
    sheets: tuple[SheetPlan, ...]
    mode: OutputMode = OutputMode.SEPARATE_FILES


def prepare_output_plan(
    outputs: Sequence[TemplateOutput],
    sources: Mapping[ProductGroup, GroupOutputSource],
    *,
    current_date: str | None = None,
    selected: Set[ProductGroup] | None = None,
) -> tuple[WorkbookPlan, ...]:
    """Проверить весь выбор до преобразования; пустой пакет сохраняет лист."""
    current_date = current_date or date.today().isoformat()
    selected = sources.keys() if selected is None else selected
    outputs = deepcopy(outputs)
    validate_outputs(
        outputs,
        selected,
        schemas={group: source.fields for group, source in sources.items()},
        current_date=current_date,
    )
    return tuple(book for output in outputs for book in _prepare_template(output, sources, selected, current_date))


def _prepare_template(
    output: TemplateOutput,
    sources: Mapping[ProductGroup, GroupOutputSource],
    selected: Set[ProductGroup],
    current_date: str,
) -> list[WorkbookPlan]:
    groups = (group for group in output.groups if group.id in selected)
    template_id = output.template_id
    sheets = [_prepare_sheet(template_id, group, sources[group.id]) for group in groups]
    return _place_sheets(output, tuple(sheets), current_date)


def _place_sheets(output: TemplateOutput, sheets: tuple[SheetPlan, ...], current_date: str) -> list[WorkbookPlan]:
    if not sheets:
        return []
    if output.mode == OutputMode.WORKBOOK_SHEETS:
        name = output_file_name(output.file_name or '', current_date, output.template_id)
        return [WorkbookPlan(output.template_id, name, sheets, output.mode)]
    return [
        WorkbookPlan(
            output.template_id,
            output_file_name(sheet.settings.file_name or '', current_date, output.template_id),
            (sheet,),
        )
        for sheet in sheets
    ]


def _prepare_sheet(template_id: str, group: GroupOutput, source: GroupOutputSource) -> SheetPlan:
    return SheetPlan(group, source.prepare(template_id, group), source.title_fields)
