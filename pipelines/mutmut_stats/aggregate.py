"""Aggregate classified mutants into a deterministic analysis."""

from collections import Counter, defaultdict
from pathlib import Path

from . import models
from .classify import classify_diff
from .diffs import make_diff
from .load import load_raw_mutants


def build_analysis(mutants_dir: Path) -> models.Analysis:
    """Collect statistics from a mutmut mutants/ directory."""
    records = tuple(_enrich(raw) for raw in load_raw_mutants(mutants_dir))
    interesting = sort_records(
        tuple(record for record in records if record.status in models.INTERESTING_STATUSES),
    )
    return models.Analysis(
        summary=_summary(records),
        mutation_score=_mutation_score(records),
        by_file=_count_rows(tuple(item.source_path for item in interesting)),
        by_function=_count_rows(tuple(item.function for item in interesting)),
        by_kind=_count_rows(tuple(item.kind for item in interesting)),
        by_change=_change_rows(interesting),
        interesting=interesting,
    )


def sort_records(records: tuple[models.MutantRecord, ...]) -> tuple[models.MutantRecord, ...]:
    """Stable order: file, function, mutant index, name."""
    return tuple(
        sorted(
            records,
            key=lambda record: (
                record.source_path,
                record.function,
                models.mutant_index(record.name),
                record.name,
            ),
        ),
    )


def _enrich(raw: models.RawMutant) -> models.MutantRecord:
    diff = make_diff(raw)
    kind, change = classify_diff(diff)
    return models.MutantRecord(
        name=raw.name,
        status=models.status_from_exit_code(raw.exit_code),
        source_path=raw.source_path,
        function=models.function_from_mutant_name(raw.name),
        kind=kind,
        change=change,
        tests=raw.tests,
        diff=diff,
    )


def _summary(records: tuple[models.MutantRecord, ...]) -> tuple[tuple[str, int], ...]:
    counts = Counter(record.status for record in records)
    ordered = [(status, counts[status]) for status in models.SUMMARY_STATUS_ORDER if counts[status]]
    leftover = sorted(set(counts) - set(models.SUMMARY_STATUS_ORDER))
    extra = [(status, counts[status]) for status in leftover]
    return tuple([("total", len(records)), *ordered, *extra])


def _mutation_score(records: tuple[models.MutantRecord, ...]) -> float:
    killed = sum(record.status == "killed" for record in records)
    survived = sum(record.status == "survived" for record in records)
    denominator = killed + survived
    if not denominator:
        return 0.0
    return killed / denominator


def _count_rows(keys: tuple[str, ...]) -> tuple[models.CountRow, ...]:
    counts = Counter(keys)
    ordered = sorted(counts, key=lambda key: (-counts[key], key))
    return tuple(models.CountRow(key=key, count=counts[key]) for key in ordered)


def _change_rows(records: tuple[models.MutantRecord, ...]) -> tuple[models.ChangeRow, ...]:
    grouped: dict[tuple[str, str], list[str]] = defaultdict(list)
    for record in records:
        grouped[(record.kind, record.change)].append(record.function)
    rows = [
        models.ChangeRow(
            kind=kind,
            change=change,
            count=len(functions),
            functions=tuple(sorted(set(functions))),
        )
        for (kind, change), functions in grouped.items()
    ]
    return tuple(sorted(rows, key=lambda row: (-row.count, row.kind, row.change)))
