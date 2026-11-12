"""Подготовка книг и листов без файлового ввода-вывода."""

from collections.abc import Mapping, Sequence, Set
from copy import deepcopy
from dataclasses import dataclass
from datetime import date
from itertools import chain
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

    @classmethod
    def from_source(cls, template_id: str, group: GroupOutput, source: GroupOutputSource) -> SheetPlan:
        """Подготовить модель к записи по правилам конкретного листа."""
        return cls(group, source.prepare(template_id, group), source.title_fields)


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
    selections: Mapping[str, Set[ProductGroup]] | None = None,
    skip_empty: bool = False,
) -> tuple[WorkbookPlan, ...]:
    """Проверить весь выбор; при skip_empty пропустить группы без выходных строк."""
    current_date = current_date or date.today().isoformat()
    selected = sources.keys() if selected is None else selected
    outputs = deepcopy(outputs)
    validate_outputs(
        outputs,
        selected,
        schemas=_schemas(sources),
        current_date=current_date,
        selections=selections,
    )
    selections = selections or {output.template_id: selected for output in outputs}
    return tuple(
        chain.from_iterable(
            _prepare_template(output, sources, selections[output.template_id], current_date, skip_empty)
            for output in outputs
        )
    )


def _schemas(sources: Mapping[ProductGroup, GroupOutputSource]) -> dict[ProductGroup, Set[str]]:
    return {group: source.fields for group, source in sources.items()}


def _prepare_template(
    output: TemplateOutput,
    sources: Mapping[ProductGroup, GroupOutputSource],
    selected: Set[ProductGroup],
    current_date: str,
    skip_empty: bool,
) -> list[WorkbookPlan]:
    groups = (group for group in output.groups if group.id in selected)
    template_id = output.template_id
    sheets = [SheetPlan.from_source(template_id, group, sources[group.id]) for group in groups]
    if skip_empty:
        sheets = [sheet for sheet in sheets if sheet.rows]
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
