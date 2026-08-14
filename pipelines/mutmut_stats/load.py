"""Read mutmut cache files from mutants/."""

import json
from collections.abc import Mapping
from pathlib import Path

from .models import RawMutant, mangled_name, mutant_index

_STATS_FILE = "mutmut-stats.json"
_TESTS_KEY = "tests_by_mangled_function_name"
_EXIT_CODES_KEY = "exit_code_by_key"


def load_raw_mutants(mutants_dir: Path) -> tuple[RawMutant, ...]:
    """Load every mutant recorded in *.meta files, in stable order."""
    tests_map = _load_tests_map(mutants_dir)
    records: list[RawMutant] = []
    for meta_path in _meta_paths(mutants_dir):
        records.extend(_raw_from_meta(mutants_dir, meta_path, tests_map))
    return tuple(sorted(records, key=_raw_sort_key))


def _meta_paths(mutants_dir: Path) -> tuple[Path, ...]:
    return tuple(sorted(mutants_dir.rglob("*.meta")))


def _load_tests_map(mutants_dir: Path) -> dict[str, tuple[str, ...]]:
    stats_path = mutants_dir / _STATS_FILE
    if not stats_path.exists():
        return {}
    payload = json.loads(stats_path.read_text(encoding="utf-8"))
    raw_tests = payload.get(_TESTS_KEY, {})
    if not isinstance(raw_tests, dict):
        return {}
    return _sorted_tests_map(raw_tests)


def _sorted_tests_map(raw_tests: Mapping[str, object]) -> dict[str, tuple[str, ...]]:
    mapped: dict[str, tuple[str, ...]] = {}
    for key in sorted(raw_tests):
        values = raw_tests[key]
        if isinstance(values, list):
            mapped[key] = tuple(sorted(str(item) for item in values))
    return mapped


def _raw_from_meta(
    mutants_dir: Path,
    meta_path: Path,
    tests_map: Mapping[str, tuple[str, ...]],
) -> tuple[RawMutant, ...]:
    source_path = meta_path.relative_to(mutants_dir).with_suffix("").as_posix()
    payload = json.loads(meta_path.read_text(encoding="utf-8"))
    exit_codes = payload.get(_EXIT_CODES_KEY, {})
    if not isinstance(exit_codes, dict):
        return ()
    spans = _load_spans(mutants_dir / f"{source_path}.spans")
    mutated_lines = _read_mutated_lines(mutants_dir / source_path)
    return tuple(
        _build_raw(
            name=str(name),
            source_path=source_path,
            exit_code=_as_exit_code(exit_code),
            tests_map=tests_map,
            spans=spans,
            mutated_lines=mutated_lines,
        )
        for name, exit_code in exit_codes.items()
    )


def _build_raw(
    name: str,
    source_path: str,
    exit_code: int | None,
    tests_map: Mapping[str, tuple[str, ...]],
    spans: Mapping[str, tuple[int, int]],
    mutated_lines: tuple[str, ...],
) -> RawMutant:
    generated = name.rsplit(".", maxsplit=1)[-1]
    orig_name = f"{mangled_name(generated)}__mutmut_orig"
    return RawMutant(
        name=name,
        source_path=source_path,
        exit_code=exit_code,
        tests=tests_map.get(mangled_name(name), ()),
        orig_source=_slice_source(mutated_lines, spans.get(orig_name)),
        mutant_source=_slice_source(mutated_lines, spans.get(generated)),
    )


def _load_spans(spans_path: Path) -> dict[str, tuple[int, int]]:
    if not spans_path.exists():
        return {}
    payload = json.loads(spans_path.read_text(encoding="utf-8"))
    raw_spans = payload.get("spans", {})
    if not isinstance(raw_spans, dict):
        return {}
    return {str(key): (int(span[0]), int(span[1])) for key, span in raw_spans.items()}


def _read_mutated_lines(mutated_path: Path) -> tuple[str, ...]:
    if not mutated_path.exists():
        return ()
    return tuple(mutated_path.read_text(encoding="utf-8").splitlines(keepends=True))


def _slice_source(lines: tuple[str, ...], span: tuple[int, int] | None) -> str:
    if span is None or not lines:
        return ""
    start, end = span
    return "".join(lines[start - 1 : end])


def _as_exit_code(value: object) -> int | None:
    if isinstance(value, int):
        return value
    return None


def _raw_sort_key(raw: RawMutant) -> tuple[str, str, int]:
    return (raw.source_path, raw.name, mutant_index(raw.name))
