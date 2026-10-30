"""
Точка входа пользовательского интерфейса.
1. разбор позиций всех активных поставщиков
2. Формирование прайсов (для внутреннего использования, для дрома и т.д.)
3. Отчёт о дублях
4...

Неинтерактивно (для Django и других скриптов)::

    uv run pf parse --json
    uv run pf parse --json --all-result
    uv run pf parse --json --result-template for_drom
    uv run pf doubles --json
    uv run pf zapaska_load_api_data --json
    uv run pf four_tochki_load_api_data --json
    uv run pf mim_load_api_data --json
    uv run pf fetch_mail_prices --json
    uv run pf get_supliers --json
    uv run pf get_product_types --json
    uv run pf get_vendors --json
    uv run pf toggle_vendor poshk --json
    uv run pf load_supplier_prices={"1": "/full/path/any_price_name.xls"}
    uv run pf load_config=/full/path/settings_dir

JSON печатается в stdout, логи в этом режиме не выводятся. Прайсы пишутся в jsonl вместо xlsx.
Код выхода 0 при успехе, 1 при ошибке.
"""

import logging
import pydoc
import sys

from app.run_argv import (
    DOUBLES,
    FETCH_MAIL_PRICES,
    FOUR_TOCHKI_LOAD_API_DATA,
    JSON_ONLY_COMMANDS,
    MIM_LOAD_API_DATA,
    PARSE,
    UPDATE_ALL_SUPPLIER_PRICES,
    ZAPASKA_LOAD_API_DATA,
    is_machine_argv,
    parse_machine_args,
)
from app.run_dialog import AnswerResult, ask_action, colorize_markdown
from app.run_machine import fail_unknown_result_template, machine_json, upload_four_tochki_data
from cfg import init_cfg
from domain.exceptions import CoreExceptionError
from infrastructure.config.result_folder import clear_result_folder
from services.async_utils import try_call
from services.configure import configure_services
from services.doubles_service import DoublesService
from services.help_service import HelpService
from services.mail_service import MailService
from services.mim_service import MimService
from services.parse_orchestrator import ParseOrchestrator
from services.price_report import PriceReportService
from services.price_schema_service import PriceSchemaService
from services.service_provider import ServiceProvider
from services.zapaska_service import ZapaskaService

logger = logging.getLogger(__name__)


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
            vendor_folder=getattr(args, 'folder', None),
        )
    return _machine_human(command, result_template)


def _machine_human(command: str, result_template: str | None) -> int:
    """Те же действия, что в меню, без JSON."""
    handlers = {
        PARSE: run_make_price_by_supplier,
        DOUBLES: run_report_doubles,
        ZAPASKA_LOAD_API_DATA: run_upload_zapaska_data,
        FOUR_TOCHKI_LOAD_API_DATA: run_upload_four_tochki_data,
        MIM_LOAD_API_DATA: run_upload_mim_data,
        FETCH_MAIL_PRICES: run_fetch_mail_prices,
        UPDATE_ALL_SUPPLIER_PRICES: run_update_all_supplier_prices,
    }
    extra: dict[str, str | None] = {}
    if command == PARSE:
        extra['result_template'] = result_template
    return 0 if try_call(handlers[command], **extra) else 1


def response_processing() -> bool:
    """Ask questions"""
    action = ask_action()
    if action is AnswerResult.EXIT:
        return False
    handlers = {
        AnswerResult.MAKE_PRICE_BY_SUPPLIER: run_make_price_by_supplier,
        AnswerResult.UPDATE_ALL_SUPPLIER_PRICES: run_update_all_supplier_prices,
        AnswerResult.SHOW_HELP: run_show_help,
    }
    try_call(handlers[action])
    return True


def run_make_price_by_supplier(*, result_template: str | None = None) -> None:
    """Make common price list by price list supplier's"""
    parse_result = ServiceProvider.resolve(ParseOrchestrator).parse_all()
    ServiceProvider.resolve(PriceReportService).write_prices(parse_result.parsed_items, template=result_template)


def run_upload_zapaska_data() -> None:
    """Load zapaska data from api"""
    with ServiceProvider.resolve(PriceSchemaService).guard():
        ServiceProvider.resolve(ZapaskaService).upload_data()
    logger.info('*** Данные успешно загружены. ***\n')


def run_upload_four_tochki_data() -> None:
    """Load Four Tochki data from api"""
    with ServiceProvider.resolve(PriceSchemaService).guard():
        upload_four_tochki_data()
    logger.info('*** Данные Форточек успешно загружены. ***\n')


def run_upload_mim_data() -> None:
    """Load MIM data from api"""
    with ServiceProvider.resolve(PriceSchemaService).guard():
        ServiceProvider.resolve(MimService).upload_data()
    logger.info('*** Данные МИМ успешно загружены. ***\n')


def run_report_doubles() -> None:
    """Parse supplier prices and write duplicates report."""
    report = ServiceProvider.resolve(DoublesService).make_report()
    logger.info(f'*** Отчёт о дублях сформирован. ***\n{report.path}\n')


def run_fetch_mail_prices() -> None:
    """Download supplier prices from the mail box."""
    with ServiceProvider.resolve(PriceSchemaService).guard():
        fetched = ServiceProvider.resolve(MailService).fetch_prices()
    logger.info(f'*** Прайсы из почты получены: {len(fetched)}. ***\n')


def run_update_all_supplier_prices() -> None:
    """Обновить прайсы всех поставщиков: запаска, Форточки и МИМ по API, затем почта.

    Сбой одного источника не отменяет остальные (ошибка логируется в try_call), но в конце
    поднимается ошибка домена, чтобы код возврата не скрывал частичный сбой.
    Схемы прайсов сравниваются один раз: копия до первого источника, проверка после последнего.
    """
    with ServiceProvider.resolve(PriceSchemaService).guard():
        updates = (
            run_upload_zapaska_data,
            run_upload_four_tochki_data,
            run_upload_mim_data,
            run_fetch_mail_prices,
        )
        failed = [update.__name__ for update in updates if not try_call(update)]
    if failed:
        names = ', '.join(failed)
        raise CoreExceptionError(f'Не обновлены источники прайсов: {names}')


def run_show_help() -> None:
    """Show user documentation (README.md) on screen, paged in a terminal."""
    text = ServiceProvider.resolve(HelpService).readme()
    if sys.stdout.isatty():
        pydoc.pager(colorize_markdown(text))
    else:
        sys.stdout.write(text)


if __name__ == '__main__':
    main()
