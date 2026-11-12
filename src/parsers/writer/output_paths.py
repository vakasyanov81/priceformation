"""Резервирование путей всех форматов до записи."""

from pathlib import Path

from domain.exceptions import ConfigValidationError
from parsers.writer.output_names import output_file_name
from parsers.writer.templates.group_output import GroupOutput, OutputMode, TemplateOutput


def register_paths(output: TemplateOutput, group: GroupOutput, current_date: str, paths: dict[str, str]) -> None:
    where = f'Шаблон {output.template_id} → {group.id}'
    pattern = group.file_name if output.mode == OutputMode.SEPARATE_FILES else output.file_name
    name = output_file_name(pattern or '', current_date, where)
    owner = where if output.mode == OutputMode.SEPARATE_FILES else f'Шаблон {output.template_id}'
    _register_path(name, owner, paths, shared=output.mode == OutputMode.WORKBOOK_SHEETS)
    _register_path(jsonl_name(name, output.mode, group.id), where, paths)


def _register_path(name: str, owner: str, paths: dict[str, str], *, shared: bool = False) -> None:
    key = name.casefold()
    previous = paths.get(key)
    if previous is not None and not (shared and previous == owner):
        raise ConfigValidationError(f'{owner} → file_name: путь {name!r} уже занят: {previous}')
    paths[key] = owner


def jsonl_name(name: str, mode: OutputMode, group: object) -> str:
    stem = Path(name).stem
    if mode == OutputMode.SEPARATE_FILES:
        return f'{stem}.jsonl'
    return f'{stem}_{group}.jsonl'
