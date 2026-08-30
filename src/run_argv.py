"""Разбор аргументов неинтерактивного CLI."""

import argparse
from collections.abc import Sequence

PARSE = "parse"
DOUBLES = "doubles"
ZAPASKA = "zapaska"
MACHINE_COMMANDS = (PARSE, DOUBLES, ZAPASKA)

_HELP_FLAGS = ("-h", "--help")
_JSON_HELP = "JSON в stdout; логи не печатаются (для Django и других скриптов)."
_ALL_RESULT_HELP = "Включить позиции разбора в JSON; без флага — только статистика процесса."


def is_machine_argv(argv: Sequence[str]) -> bool:
    """Есть подкоманда или --help: не открывать интерактивное меню."""
    if not argv:
        return False
    return argv[0] in MACHINE_COMMANDS or argv[0] in _HELP_FLAGS


def parse_machine_args(argv: Sequence[str]) -> argparse.Namespace:
    """parse / doubles / zapaska и флаг --json после команды."""
    json_flag = argparse.ArgumentParser(add_help=False)
    json_flag.add_argument("--json", action="store_true", help=_JSON_HELP)
    json_flag.add_argument("--all-result", action="store_true", help=_ALL_RESULT_HELP)
    parser = argparse.ArgumentParser(
        description="Неинтерактивный запуск разбора прайсов для сторонних скриптов.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser(PARSE, parents=[json_flag], help="Разобрать прайсы поставщиков и записать файлы.")
    subparsers.add_parser(DOUBLES, parents=[json_flag], help="Разобрать прайсы и записать отчёт о дублях.")
    subparsers.add_parser(ZAPASKA, parents=[json_flag], help="Выгрузить прайсы запаски по API.")
    return parser.parse_args(list(argv))
