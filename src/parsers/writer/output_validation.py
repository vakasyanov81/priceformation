"""Проверка групповых шаблонов целиком до первого побочного эффекта записи."""

from collections.abc import Mapping, Sequence, Set
from datetime import date

from domain.exceptions import ConfigValidationError
from domain.product_groups import ProductGroup
from domain.row_item.field_registry import FIELD_KEYS
from parsers.writer.jsonl_schema import positive_integer
from parsers.writer.output_paths import register_paths
from parsers.writer.output_structure import validate_structure
from parsers.writer.templates.group_output import GroupOutput, TemplateOutput


def validate_outputs(
    outputs: Sequence[TemplateOutput],
    selected: Set[ProductGroup],
    *,
    schemas: Mapping[ProductGroup, Set[str]] | None = None,
    current_date: str | None = None,
    selections: Mapping[str, Set[ProductGroup]] | None = None,
) -> None:
    """Проверить покрытие выбора, схемы преобразователей и общие пути XLSX/JSONL.

    Schemas содержит поля доступных выходных преобразователей. Явное подмножество
    передаётся через selected; отсутствие группы в шаблоне не сокращает выбор.
    """
    schemas = {ProductGroup.TIRE_AND_DISK: frozenset(FIELD_KEYS)} if schemas is None else schemas
    current_date = current_date or date.today().isoformat()
    paths: dict[str, str] = {}
    if len({output.template_id for output in outputs}) != len(outputs):
        raise ConfigValidationError('Повтор template_id в плане записи')
    selections = selections or {output.template_id: selected for output in outputs}
    for output in outputs:
        _validate_template(output, selections[output.template_id], schemas, current_date, paths)


def _validate_template(
    output: TemplateOutput,
    selected: Set[ProductGroup],
    schemas: Mapping[ProductGroup, Set[str]],
    current_date: str,
    paths: dict[str, str],
) -> None:
    validate_structure(output, selected)
    for group in output.groups:
        _validate_group(group, schemas, f'Шаблон {output.template_id} → {group.id}')
        register_paths(output, group, current_date, paths if group.id in selected else {})


def _validate_group(group: GroupOutput, schemas: Mapping[ProductGroup, Set[str]], where: str) -> None:
    if not positive_integer(group.schema_version):
        raise ConfigValidationError(f'{where} → schema_version: требуется положительное целое число')
    fields = schemas.get(group.id)
    if fields is None:
        raise ConfigValidationError(f'{where}: нет доступного преобразователя группы')
    _validate_columns(group, fields, where)
    for field in group.filters:
        _validate_field(field, fields, f'{where} → filters')
    for rule in group.formatting.get('rules') or [group.formatting]:
        _validate_field(rule.get('by_column'), fields, f'{where} → formatting → by_column')


def _validate_field(field: object, fields: Set[str], where: str) -> None:
    if field is not None and (not isinstance(field, str) or field not in fields):
        raise ConfigValidationError(f'{where}: неизвестное поле {field!r}')


def _validate_columns(group: GroupOutput, fields: Set[str], where: str) -> None:
    for index, column in enumerate(group.columns):
        if len(column) != 1:
            raise ConfigValidationError(f'{where} → columns[{index}]: требуется одна колонка')
        settings = next(iter(column.values()))
        for key in ('field', 'suffix_when'):
            _validate_field(settings.get(key), fields, f'{where} → columns[{index}] → {key}')
