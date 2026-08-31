"""Разбор аргументов неинтерактивного CLI."""

import argparse
from collections.abc import Sequence
from typing import Any, cast

from parsers.writer.templates.all_templates import writer_templates_by_name

PARSE = "parse"
DOUBLES = "doubles"
ZAPASKA = "zapaska"
GET_SUPLIERS = "get_supliers"
LOAD_SUPPLIER_PRICES = "load_supplier_prices"
MACHINE_COMMANDS = (PARSE, DOUBLES, ZAPASKA, GET_SUPLIERS, LOAD_SUPPLIER_PRICES)
JSON_ONLY_COMMANDS = frozenset((GET_SUPLIERS, LOAD_SUPPLIER_PRICES))
_LOAD_INLINE_PREFIX = f"{LOAD_SUPPLIER_PRICES}="
_PRICES_HELP = 'JSON-объект {"ИД или sup_code": "путь к xls или xlsx"}.'

_HELP_FLAGS = ("-h", "--help")
_JSON_HELP = "JSON в stdout; прайсы в jsonl; логи не печатаются (для Django и других скриптов)."
_ALL_RESULT_HELP = "Включить позиции разбора в JSON; без флага — только статистика процесса."
_CLEAR_RESULT_HELP = "Удалить всё из папки result перед записью новых файлов."


def is_machine_argv(argv: Sequence[str]) -> bool:
    """Есть подкоманда или --help: не открывать интерактивное меню."""
    expanded = _expand_inline_prices(argv)
    if not expanded:
        return False
    command = expanded[0]
    return command in MACHINE_COMMANDS or command in _HELP_FLAGS


def parse_machine_args(argv: Sequence[str]) -> argparse.Namespace:
    """parse / doubles / zapaska / get_supliers / load_supplier_prices и флаг --json."""
    json_flag = _json_flags()
    parser = argparse.ArgumentParser(
        description="Неинтерактивный запуск разбора прайсов для сторонних скриптов.",
    )
    _attach_commands(parser, json_flag)
    return parser.parse_args(_expand_inline_prices(argv))


def _json_flags() -> argparse.ArgumentParser:
    json_flag = argparse.ArgumentParser(add_help=False)
    json_flag.add_argument("--json", action="store_true", help=_JSON_HELP)
    json_flag.add_argument("--all-result", action="store_true", help=_ALL_RESULT_HELP)
    json_flag.add_argument("--clear-previous-result", action="store_true", help=_CLEAR_RESULT_HELP)
    return json_flag


def _attach_commands(parser: argparse.ArgumentParser, json_flag: argparse.ArgumentParser) -> None:
    subparsers = parser.add_subparsers(dest="command", required=True)
    parse_cmd = _json_parser(subparsers, json_flag, PARSE, "Разобрать прайсы поставщиков и записать файлы.")
    parse_cmd.add_argument(
        "--result-template",
        default=None,
        metavar="NAME",
        help=_result_template_help(),
    )
    _json_parser(subparsers, json_flag, DOUBLES, "Разобрать прайсы и записать отчёт о дублях.")
    _json_parser(subparsers, json_flag, ZAPASKA, "Выгрузить прайсы запаски по API.")
    _json_parser(subparsers, json_flag, GET_SUPLIERS, "Получить названия поставщиков.")
    load_cmd = _json_parser(
        subparsers,
        json_flag,
        LOAD_SUPPLIER_PRICES,
        "Загрузить прайсы поставщиков в file_prices.",
    )
    load_cmd.add_argument("prices", help=_PRICES_HELP)


def _json_parser(
    subparsers: Any,
    json_flag: argparse.ArgumentParser,
    command: str,
    help_text: str,
) -> argparse.ArgumentParser:
    return cast(argparse.ArgumentParser, subparsers.add_parser(command, parents=[json_flag], help=help_text))


def _expand_inline_prices(argv: Sequence[str]) -> list[str]:
    """load_supplier_prices={...} → команда и JSON-аргумент."""
    if not argv:
        return []
    first = argv[0]
    if not first.startswith(_LOAD_INLINE_PREFIX):
        return list(argv)
    return [LOAD_SUPPLIER_PRICES, first.removeprefix(_LOAD_INLINE_PREFIX), *argv[1:]]


def _result_template_help() -> str:
    names = ", ".join(writer_templates_by_name())
    return f"Шаблон записи результата ({names}). Без флага — все шаблоны."
