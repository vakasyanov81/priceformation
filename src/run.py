"""
Точка входа пользовательского интерфейса.
1. разбор позиций всех активных поставщиков
2. Формирование прайсов (для внутреннего использования, для дрома и т.д.)
3. Отчёт о дублях
4...

Неинтерактивно (для Django и других скриптов)::

    python src/run.py parse --json
    python src/run.py parse --json --all-result
    python src/run.py parse --json --result-template for_drom
    python src/run.py doubles --json
    python src/run.py zapaska_load_api_data --json
    python src/run.py get_supliers --json
    python src/run.py load_supplier_prices={"1": "/full/path/any_price_name.xls"}
    python src/run.py load_config=/full/path/settings_dir

JSON печатается в stdout, логи в этом режиме не выводятся. Прайсы пишутся в jsonl вместо xlsx.
Код выхода 0 при успехе, 1 при ошибке.
"""

import sys

from cfg import init_cfg
from core.async_utils import try_call
from core.log_message import print_log
from core.parse_paths import clear_result_folder
from run_argv import DOUBLES, JSON_ONLY_COMMANDS, PARSE, ZAPASKA_LOAD_API_DATA, is_machine_argv, parse_machine_args
from run_dialog import AnswerResult, ask_action
from run_machine import fail_unknown_result_template, machine_json
from services.configure import configure_services
from services.doubles_service import DoublesService
from services.parse_orchestrator import ParseOrchestrator
from services.price_report import PriceReportService
from services.service_provider import ServiceProvider
from services.zapaska_service import ZapaskaService


def main() -> None:
    """entry point"""
    init_cfg()
    configure_services()
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
    result_template = getattr(args, 'result_template', None)
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
            supplier_prices=getattr(args, 'prices', None),
            config_path=getattr(args, 'config', None),
        )
    return _machine_human(command, result_template)


def _machine_human(command: str, result_template: str | None) -> int:
    """Те же действия, что в меню, без JSON."""
    handlers = {
        PARSE: run_make_price_by_supplier,
        DOUBLES: run_report_doubles,
        ZAPASKA_LOAD_API_DATA: run_upload_zapaska_data,
    }
    extra: dict[str, str | None] = {}
    if command == PARSE:
        extra['result_template'] = result_template
    try_call(handlers[command], **extra)
    return 0


def response_processing() -> bool:
    """Ask questions"""
    match ask_action():
        case AnswerResult.MAKE_PRICE_BY_SUPPLIER:
            try_call(run_make_price_by_supplier)
        case AnswerResult.UPDATE_ZAPASKA_DATA:
            try_call(run_upload_zapaska_data)
        case AnswerResult.REPORT_DOUBLES:
            try_call(run_report_doubles)
        case AnswerResult.EXIT:
            return False
    return True


def run_make_price_by_supplier(*, result_template: str | None = None) -> None:
    """Make common price list by price list supplier's"""
    parse_result = ServiceProvider.resolve(ParseOrchestrator).parse_all()
    ServiceProvider.resolve(PriceReportService).write_prices(parse_result.parsed_items, template=result_template)


def run_upload_zapaska_data() -> None:
    """Load zapaska data from api"""
    ServiceProvider.resolve(ZapaskaService).upload_data()
    print_log('*** Данные успешно загружены. ***\n')


def run_report_doubles() -> None:
    """Parse supplier prices and write duplicates report."""
    report = ServiceProvider.resolve(DoublesService).make_report()
    print_log(f'*** Отчёт о дублях сформирован. ***\n{report.path}\n')


if __name__ == '__main__':
    main()
