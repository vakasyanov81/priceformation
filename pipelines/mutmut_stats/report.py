"""Markdown and JSON renderers for mutmut analysis."""

import json
from collections.abc import Mapping, Sequence

from .aggregate import sort_records
from .models import Analysis, ChangeRow, CountRow, MutantRecord

_MAX_FUNCTIONS = 8


def render_markdown(analysis: Analysis) -> str:
    """Human-readable report focused on surviving mutants."""
    sections = (
        "# Статистика mutmut",
        "",
        _summary_section(analysis),
        _table_section("Выжившие по файлам", "файл", analysis.by_file),
        _table_section("Выжившие по функциям", "функция", analysis.by_function),
        _table_section("Выжившие по типу мутации", "тип", analysis.by_kind),
        _changes_section(analysis.by_change),
        _cards_section(sort_records(analysis.interesting)),
    )
    return "\n".join(sections).rstrip() + "\n"


def render_json(analysis: Analysis) -> str:
    """Machine-readable report with sorted keys."""
    payload = {
        "summary": dict(analysis.summary),
        "mutation_score": analysis.mutation_score,
        "by_file": _rows_as_dicts(analysis.by_file),
        "by_function": _rows_as_dicts(analysis.by_function),
        "by_kind": _rows_as_dicts(analysis.by_kind),
        "by_change": [_change_dict(row) for row in analysis.by_change],
        "interesting": [_record_dict(record) for record in sort_records(analysis.interesting)],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _summary_section(analysis: Analysis) -> str:
    percent = f"{analysis.mutation_score * 100:.1f}"
    lines = [
        "## Сводка",
        "",
        "| статус | число |",
        "| --- | ---: |",
    ]
    lines.extend(f"| {status} | {count} |" for status, count in analysis.summary)
    lines.extend(
        (
            "",
            f"**Mutation score:** {percent}% (`killed / (killed + survived)`)",
            "",
        ),
    )
    return "\n".join(lines)


def _table_section(title: str, column: str, rows: Sequence[CountRow]) -> str:
    if not rows:
        return f"## {title}\n\nНет записей.\n"
    lines = [
        f"## {title}",
        "",
        f"| {column} | число |",
        "| --- | ---: |",
    ]
    lines.extend(f"| `{row.key}` | {row.count} |" for row in rows)
    return "\n".join(lines) + "\n"


def _changes_section(rows: Sequence[ChangeRow]) -> str:
    title = "Одинаковые изменения"
    if not rows:
        return f"## {title}\n\nНет записей.\n"
    lines = [
        f"## {title}",
        "",
        "| изменение | тип | число | функции |",
        "| --- | --- | ---: | --- |",
    ]
    lines.extend(_change_table_row(row) for row in rows)
    return "\n".join(lines) + "\n"


def _change_table_row(row: ChangeRow) -> str:
    functions = _format_functions(row.functions)
    return f"| `{row.change}` | {row.kind} | {row.count} | {functions} |"


def _format_functions(functions: Sequence[str]) -> str:
    if len(functions) <= _MAX_FUNCTIONS:
        return ", ".join(f"`{name}`" for name in functions)
    shown = ", ".join(f"`{name}`" for name in functions[:_MAX_FUNCTIONS])
    rest = len(functions) - _MAX_FUNCTIONS
    return f"{shown}, … +{rest}"


def _cards_section(records: Sequence[MutantRecord]) -> str:
    if not records:
        return "## Карточки мутантов\n\nНет выживших и прочих интересных мутантов.\n"
    blocks = ["## Карточки мутантов", ""]
    for record in records:
        blocks.append(_card(record))
    return "\n".join(blocks)


def _card(record: MutantRecord) -> str:
    tests = _format_tests(record.tests)
    hint = _hint(record)
    diff = record.diff or "(нет diff: в mutants/ нет исходника или .spans)"
    lines = [
        f"### `{record.name}` — {record.status}",
        "",
        f"- файл: `{record.source_path}`",
        f"- функция: `{record.function}`",
        f"- изменение: {record.kind} `{record.change}`",
        f"- тесты ({len(record.tests)}): {tests}",
    ]
    if hint:
        lines.append(f"- подсказка: {hint}")
    lines.extend(("", "```diff", diff, "```", ""))
    return "\n".join(lines)


def _format_tests(tests: Sequence[str]) -> str:
    if not tests:
        return "нет в `mutmut-stats.json` (функция не вызывалась тестами)"
    return ", ".join(f"`{name}`" for name in tests)


def _hint(record: MutantRecord) -> str:
    if not record.tests:
        return "тесты, похоже, не входят в эту функцию — мутант не из чего убивать"
    if record.kind == "string_case":
        return "часто эквивалентный мутант: смена регистра строки не меняет поведение"
    if record.kind == "string_wrap":
        return "проверьте, не эквивалентна ли обёртка XX (кавычки, пустые строки, разделители)"
    if record.kind == "to_none" and "encoding" in record.diff:
        return "encoding=None часто ведёт себя как utf-8 по умолчанию"
    return ""


def _rows_as_dicts(rows: Sequence[CountRow]) -> list[Mapping[str, object]]:
    return [{"key": row.key, "count": row.count} for row in rows]


def _change_dict(row: ChangeRow) -> dict[str, object]:
    return {
        "kind": row.kind,
        "change": row.change,
        "count": row.count,
        "functions": list(row.functions),
    }


def _record_dict(record: MutantRecord) -> dict[str, object]:
    return {
        "name": record.name,
        "status": record.status,
        "source_path": record.source_path,
        "function": record.function,
        "kind": record.kind,
        "change": record.change,
        "tests": list(record.tests),
        "diff": record.diff,
    }
