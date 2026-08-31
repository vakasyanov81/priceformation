"""
Точка входа пользовательского интерфейса.
1. разбор позиций всех активных поставщиков
2. Формирование прайсов (для внутреннего использования, для дрома и т.д.)
3. Отчёт о дублях
4...

Неинтерактивно (для Django и других скриптов)::

    python src/run.py parse --json
    python src/run.py parse --json --all-result
    python src/run.py parse --json --clear-previous-result
    python src/run.py parse --json --result-template for_drom
    python src/run.py doubles --json
    python src/run.py zapaska --json
    python src/run.py get_supliers --json
    python src/run.py load_supplier_prices={"1": "/full/path/any_price_name.xls"}
    python src/run.py load_supplier_prices={"poshk": "/full/path/any_price_name.xls"}

JSON печатается в stdout, логи в этом режиме не выводятся. Прайсы пишутся в jsonl вместо xlsx.
Код выхода 0 при успехе, 1 при ошибке.
"""

import sys

from cfg import init_cfg
from cfg.zapaska_api import get_zapaska_api_config
from core.async_utils import try_call
from core.log_message import print_log
from core.parse_paths import clear_result_folder
from parsers.all_vendors import all_vendors
from parsers.common_price import CommonPrice
from parsers.common_price_output import CommonPriceOut
from parsers.remote.zapaska_client import load_remote_vendor_data
from run_argv import DOUBLES, JSON_ONLY_COMMANDS, PARSE, ZAPASKA, is_machine_argv, parse_machine_args
from run_dialog import AnswerResult, ask_action
from run_machine import fail_unknown_result_template, machine_json


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
    result_template = getattr(args, "result_template", None)
    json_mode = bool(args.json or args.all_result or command in JSON_ONLY_COMMANDS)
    rejected = fail_unknown_result_template(command, result_template, json_mode=json_mode)
    if rejected is not None:
        return rejected
    if args.clear_previous_result:
        clear_result_folder()
    if json_mode:
        return machine_json(
            command,
            all_result=bool(args.all_result),
            result_template=result_template,
            supplier_prices=getattr(args, "prices", None),
        )
    return _machine_human(command, result_template)


def _machine_human(command: str, result_template: str | None) -> int:
    """Те же действия, что в меню, без JSON."""
    handlers = {
        PARSE: run_make_price_by_supplier,
        DOUBLES: run_report_doubles,
        ZAPASKA: run_upload_zapaska_data,
    }
    extra: dict[str, str | None] = {}
    if command == PARSE:
        extra["result_template"] = result_template
    try_call(handlers[command], **extra)
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


def run_make_price_by_supplier(*, result_template: str | None = None) -> None:
    """Make common price list by price list supplier's"""
    common_price = CommonPrice()
    common_price.parse_all_vendors(all_vendors())
    CommonPriceOut(common_price.parsed_items).write_all_prices(result_template=result_template)


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
