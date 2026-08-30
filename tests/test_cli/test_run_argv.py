"""Аргументы неинтерактивного CLI."""

import pytest

from run_argv import DOUBLES, PARSE, ZAPASKA, is_machine_argv, parse_machine_args


def test_is_machine_argv_empty() -> None:
    """без аргументов — интерактивное меню."""
    assert is_machine_argv([]) is False


def test_is_machine_argv_pytest_noise() -> None:
    """аргументы pytest не включают машинный режим."""
    assert is_machine_argv(["-n=2"]) is False
    assert is_machine_argv(["tests/test_run.py"]) is False


def test_is_machine_argv_commands() -> None:
    """подкоманды и --help включают машинный режим."""
    assert is_machine_argv([PARSE]) is True
    assert is_machine_argv([DOUBLES, "--json"]) is True
    assert is_machine_argv(["--help"]) is True
    assert is_machine_argv(["-h"]) is True


def test_parse_all_result_flag() -> None:
    """--all-result включает позиции в JSON."""
    args = parse_machine_args([PARSE, "--json", "--all-result"])
    assert args.command == PARSE
    assert args.json is True
    assert args.all_result is True


def test_parse_all_result_without_json() -> None:
    """--all-result без --json тоже распознаётся."""
    args = parse_machine_args([PARSE, "--all-result"])
    assert args.all_result is True
    assert args.json is False


def test_parse_without_json() -> None:
    """команда без --json."""
    args = parse_machine_args([ZAPASKA])
    assert args.command == ZAPASKA
    assert args.json is False
    assert args.all_result is False
    assert args.clear_previous_result is False


def test_parse_result_template_flag() -> None:
    """--result-template сохраняет имя шаблона."""
    args = parse_machine_args([PARSE, "--result-template", "for_drom"])
    assert args.command == PARSE
    assert args.result_template == "for_drom"


def test_parse_result_template_default() -> None:
    """без --result-template имя пустое."""
    args = parse_machine_args([PARSE])
    assert args.result_template is None


def test_result_template_rejected_on_doubles() -> None:
    """--result-template есть только у parse."""
    with pytest.raises(SystemExit) as exit_info:
        parse_machine_args([DOUBLES, "--result-template", "for_drom"])
    assert exit_info.value.code == 2


def test_parse_doubles() -> None:
    """команда doubles."""
    args = parse_machine_args([DOUBLES, "--json"])
    assert args.command == DOUBLES
    assert args.json is True
    assert args.all_result is False


def test_parse_clear_previous_result_flag() -> None:
    """--clear-previous-result распознаётся."""
    args = parse_machine_args([PARSE, "--json", "--clear-previous-result"])
    assert args.clear_previous_result is True
    assert args.json is True


def test_parse_help_exits() -> None:
    """--help завершает процесс с кодом 0."""
    with pytest.raises(SystemExit) as exit_info:
        parse_machine_args(["--help"])
    assert exit_info.value.code == 0


def test_parse_unknown_command_exits() -> None:
    """неизвестная команда — ошибка argparse."""
    with pytest.raises(SystemExit) as exit_info:
        parse_machine_args(["nope"])
    assert exit_info.value.code == 2
