"""Аргументы неинтерактивного CLI."""

import pytest

from run_argv import (
    DOUBLES,
    GET_SUPLIERS,
    JSON_ONLY_COMMANDS,
    LOAD_SUPPLIER_PRICES,
    PARSE,
    ZAPASKA,
    is_machine_argv,
    parse_machine_args,
)

_CONFIG_CMD = "load_config"


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
    assert is_machine_argv([GET_SUPLIERS]) is True
    assert is_machine_argv([LOAD_SUPPLIER_PRICES]) is True
    assert is_machine_argv([f'{LOAD_SUPPLIER_PRICES}={{"1": "a.xls"}}']) is True
    assert is_machine_argv([_CONFIG_CMD]) is True
    assert is_machine_argv([f"{_CONFIG_CMD}=/full/path/vendor_list.json"]) is True
    assert is_machine_argv(["--help"]) is True
    assert is_machine_argv(["-h"]) is True


def test_load_is_json_only() -> None:
    """load_supplier_prices всегда в JSON-режиме."""
    assert LOAD_SUPPLIER_PRICES in JSON_ONLY_COMMANDS


def test_load_config_is_json_only() -> None:
    """load_config всегда в JSON-режиме."""
    assert _CONFIG_CMD in JSON_ONLY_COMMANDS


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


def test_parse_get_supliers() -> None:
    """команда get_supliers."""
    args = parse_machine_args([GET_SUPLIERS, "--json"])
    assert args.command == GET_SUPLIERS
    assert args.json is True


def test_parse_load_supplier_prices() -> None:
    """команда load_supplier_prices с JSON-аргументом."""
    raw = '{"1": "/incoming/any_price_name.xls"}'
    args = parse_machine_args([LOAD_SUPPLIER_PRICES, raw])
    assert args.command == LOAD_SUPPLIER_PRICES
    assert args.prices == raw


def test_parse_load_supplier_prices_inline() -> None:
    """load_supplier_prices={...} разбирается как команда и JSON."""
    raw = '{"1": "/incoming/any_price_name.xlsx"}'
    args = parse_machine_args([f"{LOAD_SUPPLIER_PRICES}={raw}"])
    assert args.command == LOAD_SUPPLIER_PRICES
    assert args.prices == raw


def test_parse_load_supplier_prices_requires_json() -> None:
    """без JSON-карты — ошибка argparse."""
    with pytest.raises(SystemExit) as exit_info:
        parse_machine_args([LOAD_SUPPLIER_PRICES])
    assert exit_info.value.code == 2


def test_parse_load_config() -> None:
    """команда load_config с путём."""
    raw = "/incoming/vendor_list.json"
    args = parse_machine_args([_CONFIG_CMD, raw])
    assert args.command == _CONFIG_CMD
    assert args.config == raw


def test_parse_load_config_inline() -> None:
    """load_config=path разбирается как команда и путь."""
    raw = "/incoming/black_list"
    args = parse_machine_args([f"{_CONFIG_CMD}={raw}"])
    assert args.command == _CONFIG_CMD
    assert args.config == raw


def test_parse_load_config_requires_path() -> None:
    """без пути — ошибка argparse."""
    with pytest.raises(SystemExit) as exit_info:
        parse_machine_args([_CONFIG_CMD])
    assert exit_info.value.code == 2


def test_parse_load_config_folder() -> None:
    """команда load_config с путём к папке."""
    raw = "/incoming/settings"
    args = parse_machine_args([_CONFIG_CMD, raw])
    assert args.command == _CONFIG_CMD
    assert args.config == raw


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
