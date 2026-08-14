"""Unit tests for mutant diff classification."""

from difflib import unified_diff

from pipelines.mutmut_stats.classify import classify_diff


def _diff(old: str, new: str) -> str:
    return "\n".join(
        unified_diff(
            old.splitlines(),
            new.splitlines(),
            fromfile="src/sample.py",
            tofile="src/sample.py",
            lineterm="",
        ),
    )


def test_operator_equality_and_lt() -> None:
    assert classify_diff(_diff("return left == right", "return left != right")) == (
        "operator",
        "== → !=",
    )
    assert classify_diff(_diff("if value < limit:", "if value <= limit:")) == (
        "operator",
        "< → <=",
    )


def test_method_swap_and_keyword() -> None:
    assert classify_diff(_diff("name.lower()", "name.upper()")) == (
        "method_swap",
        "lower → upper",
    )
    assert classify_diff(_diff("return True", "return False")) == (
        "keyword",
        "True → False",
    )


def test_string_wrap_and_case() -> None:
    assert classify_diff(_diff('encoding="utf-8"', 'encoding="XXutf-8XX"')) == (
        "string_wrap",
        "utf-8 → XXutf-8XX",
    )
    assert classify_diff(_diff('encoding="utf-8"', 'encoding="UTF-8"')) == (
        "string_case",
        "utf-8 → UTF-8",
    )


def test_number_to_none_and_unknown() -> None:
    assert classify_diff(_diff("return 0", "return 1")) == ("number", "0 → 1")
    assert classify_diff(_diff("mark = title.strip()", "mark = None")) == (
        "to_none",
        "title.strip() → None",
    )
    assert classify_diff(_diff("def __init__(self, x):", "def __init__(None, x):")) == (
        "to_none",
        "self → None",
    )
    assert classify_diff(_diff("if not ready:", "if ready:")) == ("keyword", "not → ∅")
    assert classify_diff(_diff("value = None", 'value = ""')) == (
        "none_to_empty",
        'None → ""',
    )
    assert classify_diff("") == ("unknown", "")
