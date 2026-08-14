"""Shared tiny mutmut cache for pipeline tests."""

import json
from pathlib import Path

_SAMPLE_SOURCE = """def add(left, right):
    return left == right


def x_add__mutmut_orig(left, right):
    return left == right


def x_add__mutmut_1(left, right):
    return left != right


def x_add__mutmut_2(left, right):
    return left == None


def x_mul__mutmut_orig(left, right):
    return left * right


def x_mul__mutmut_1(left, right):
    return left / right
"""


def write_tiny_mutants(root: Path) -> Path:
    """Create a minimal mutants/ tree under root and return it."""
    mutants_dir = root / "mutants"
    source_dir = mutants_dir / "src"
    source_dir.mkdir(parents=True)
    (source_dir / "sample.py").write_text(_SAMPLE_SOURCE, encoding="utf-8")
    spans_json = json.dumps({"version": 1, "spans": _spans()})
    (source_dir / "sample.py.spans").write_text(spans_json, encoding="utf-8")
    (source_dir / "sample.py.meta").write_text(json.dumps(_meta()), encoding="utf-8")
    (mutants_dir / "mutmut-stats.json").write_text(json.dumps(_stats()), encoding="utf-8")
    return mutants_dir


def _spans() -> dict[str, list[int]]:
    names = (
        "x_add__mutmut_orig",
        "x_add__mutmut_1",
        "x_add__mutmut_2",
        "x_mul__mutmut_orig",
        "x_mul__mutmut_1",
    )
    return {name: list(_span(name)) for name in names}


def _span(func_name: str) -> tuple[int, int]:
    header = f"def {func_name}("
    for index, line in enumerate(_SAMPLE_SOURCE.splitlines(), start=1):
        if line.startswith(header):
            return index, index + 1
    raise LookupError(func_name)


def _meta() -> dict[str, object]:
    return {
        "exit_code_by_key": {
            "sample.x_add__mutmut_1": 0,
            "sample.x_add__mutmut_2": 1,
            "sample.x_mul__mutmut_1": 5,
        },
        "hash_by_function_name": {},
        "type_check_error_by_key": {},
        "durations_by_key": {},
        "estimated_durations_by_key": {},
    }


def _stats() -> dict[str, object]:
    return {
        "tests_by_mangled_function_name": {
            "sample.x_add": [
                "tests/test_sample.py::test_add_b",
                "tests/test_sample.py::test_add_a",
            ],
        },
        "duration_by_test": {},
        "stats_time": 1.0,
        "function_hashes": {},
        "function_dependencies": {},
        "config_fingerprint": {},
        "watched_file_hashes": {},
        "git_commit": None,
    }
