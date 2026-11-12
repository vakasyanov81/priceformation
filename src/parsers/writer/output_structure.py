"""Структурные инварианты группового шаблона."""

from collections.abc import Set

from domain.exceptions import ConfigValidationError
from domain.product_groups import ProductGroup
from parsers.writer.output_names import validate_sheet_name
from parsers.writer.templates.group_output import OutputMode, TemplateOutput


def validate_structure(output: TemplateOutput, selected: Set[ProductGroup]) -> None:
    """Проверить объявление групп, выбор и размещение книг."""
    where = f'Шаблон {output.template_id}'
    identifiers = [group.id for group in output.groups]
    if not output.template_id.strip() or not identifiers:
        raise ConfigValidationError(f'{where} → groups: пустое описание')
    if len(set(identifiers)) != len(identifiers):
        raise ConfigValidationError(f'{where} → groups: повтор группы')
    missing = set(selected).difference(identifiers)
    if missing:
        raise ConfigValidationError(f'{where} → groups: выбраны неподдерживаемые группы {sorted(missing)}')
    _validate_mode(output, where)
    _validate_sheets(output, where)


def _validate_mode(output: TemplateOutput, where: str) -> None:
    if output.mode not in (OutputMode.SEPARATE_FILES, OutputMode.WORKBOOK_SHEETS):
        raise ConfigValidationError(f'{where} → mode: неизвестное размещение {output.mode!r}')
    separate = output.mode == OutputMode.SEPARATE_FILES
    if separate == (output.file_name is not None):
        raise ConfigValidationError(f'{where} → file_name: имя книги не соответствует режиму')
    for group in output.groups:
        if separate != (group.file_name is not None):
            raise ConfigValidationError(f'{where} → {group.id} → file_name: имя группы не соответствует режиму')


def _validate_sheets(output: TemplateOutput, where: str) -> None:
    names: set[str] = set()
    for group in output.groups:
        validate_sheet_name(group.sheet_name, f'{where} → {group.id}')
        sheet = group.sheet_name.casefold()
        if output.mode == OutputMode.WORKBOOK_SHEETS and sheet in names:
            raise ConfigValidationError(f'{where} → {group.id} → sheet_name: повтор имени листа')
        names.add(sheet)
