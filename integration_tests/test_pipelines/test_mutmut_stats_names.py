"""Unit tests for mutmut name and status helpers."""

from pipelines.mutmut_stats.models import (
    function_from_mutant_name,
    mutant_index,
    status_from_exit_code,
)


def test_function_from_plain_and_dunder_names() -> None:
    assert function_from_mutant_name("cfg.api.x_load_dotenv__mutmut_8") == "load_dotenv"
    assert function_from_mutant_name("cfg.api.x__parse_dotenv_line__mutmut_17") == "_parse_dotenv_line"
    assert function_from_mutant_name("mod.plain__mutmut_1") == "plain"


def test_function_from_class_method() -> None:
    name = "parsers.mim.x\u01c1MimParser2Sheet\u01c1_title_chunks__mutmut_2"
    assert function_from_mutant_name(name) == "MimParser2Sheet._title_chunks"


def test_mutant_index_and_unknown_status() -> None:
    assert mutant_index("sample.x_add__mutmut_12") == 12
    assert mutant_index("sample.x_add__mutmut_orig") == 0
    assert status_from_exit_code(0) == "survived"
    assert status_from_exit_code(1) == "killed"
    assert status_from_exit_code(5) == "no tests"
    assert status_from_exit_code(None) == "not checked"
    assert status_from_exit_code(999) == "suspicious"
