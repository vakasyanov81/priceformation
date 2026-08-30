"""
Точка входа пользовательского интерфейса.
1. разбор позиций всех активных поставщиков
2. Формирование прайсов (для внутреннего использования, для дрома и т.д.)
3. Отчёт о дублях
4...

Неинтерактивно (для Django и других скриптов)::

    python src/run.py parse --json
    python src/run.py parse --json --all-result
    python src/run.py doubles --json
    python src/run.py zapaska --json

JSON печатается в stdout, логи в этом режиме не выводятся. Код выхода 0 при успехе, 1 при ошибке.
"""

import sys

from cfg import init_cfg
from cfg.zapaska_api import get_zapaska_api_config
from core.async_utils import try_call
from core.log_message import print_log
from parsers.all_vendors import all_vendors
from parsers.common_price import CommonPrice
from parsers.common_price_output import CommonPriceOut
from parsers.remote.zapaska_client import load_remote_vendor_data
from run_argv import DOUBLES, PARSE, ZAPASKA, is_machine_argv, parse_machine_args
from run_dialog import AnswerResult, ask_action
from run_machine import machine_json


def main() -> None:
    """
    entry point
    :return:
    """
    init_cfg()
    argv = sys.argv[1:]
    if is_machine_argv(argv):
        sys.exit(_run_machine(argv))
    while True:
        if not response_processing():
            break
    sys.exit(0)


def _run_machine(argv: list[str]) -> int:
    """Неинтерактивная команда: JSON или человекочитаемый вывод."""
    args = parse_machine_args(argv)
    command = args.command
    if not isinstance(command, str):
        return 1
    if args.json or args.all_result:
        return machine_json(command, all_result=bool(args.all_result))
    return _machine_human(command)


def _machine_human(command: str) -> int:
    """Те же действия, что в меню, без JSON."""
    handlers = {
        PARSE: run_make_price_by_supplier,
        DOUBLES: run_report_doubles,
        ZAPASKA: run_upload_zapaska_data,
    }
    try_call(handlers[command])
    return 0


def response_processing() -> bool:
    """Ask questions"""
    continuation_of_execution = True
    match ask_action():
        case AnswerResult.MAKE_PRICE_BY_SUPPLIER:
            try_call(run_make_price_by_supplier)
        case AnswerResult.UPDATE_ZAPASKA_DATA:
            try_call(run_upload_zapaska_data)
        case AnswerResult.REPORT_DOUBLES:
            try_call(run_report_doubles)
        case AnswerResult.EXIT:
            continuation_of_execution = False
    return continuation_of_execution


def run_make_price_by_supplier() -> None:
    """Make common price list by price list supplier's"""
    common_price = CommonPrice()
    common_price.parse_all_vendors(all_vendors())
    CommonPriceOut(common_price.parsed_items).write_all_prices()


def run_upload_zapaska_data() -> None:
    """Load zapaska data from api"""
    load_remote_vendor_data(api=get_zapaska_api_config())
    print_log("*** Данные успешно загружены. ***\n")


def run_report_doubles() -> None:
    """Parse supplier prices and write duplicates report."""
    common_price = CommonPrice()
    common_price.parse_all_vendors(all_vendors())
    report_path = CommonPriceOut(common_price.parsed_items).write_doubles_report()
    print_log(f"*** Отчёт о дублях сформирован. ***\n{report_path}\n")


if __name__ == "__main__":
    main()
