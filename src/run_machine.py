"""JSON-режим CLI: разбор прайса и ответ в stdout."""

import logging
import time
from collections.abc import Mapping
from typing import Any

from core.log_message import print_log, set_print_quiet
from parse_report import JsonReport, emit_json, error_payload
from parse_report_build import report_from_result
from parsers.all_vendors import all_vendor_supplier_catalog
from parsers.common_price_output import jsonl_output_files
from parsers.load_config import load_config
from parsers.load_supplier_prices import catalog_entry_for, load_supplier_prices, parse_prices_json
from parsers.writer.templates.all_templates import UnknownWriterTemplateError, get_writer_template
from run_argv import DOUBLES, GET_SUPLIERS, LOAD_CONFIG, LOAD_SUPPLIER_PRICES, PARSE, ZAPASKA_LOAD_API_DATA
from services import doubles_service, zapaska_service
from services.configure import ensure_services_configured
from services.parse_orchestrator import ParseOrchestrator
from services.price_report import PriceReportService
from services.service_provider import ServiceProvider

_INTERRUPT = 'interrupted'
_COMPACT_ERROR_COMMANDS = frozenset((LOAD_SUPPLIER_PRICES, LOAD_CONFIG, ZAPASKA_LOAD_API_DATA))


def fail_unknown_result_template(
    command: str,
    name: str | None,
    *,
    json_mode: bool,
) -> int | None:
    """Если имя шаблона задано и неизвестно — ответ с ошибкой и код 1."""
    if name is None:
        return None
    started = time.monotonic()
    try:
        get_writer_template(name)
    except UnknownWriterTemplateError as exc:
        if json_mode:
            emit_json(
                error_payload(command, type(exc).__name__, str(exc)),
                started=started,
            )
        else:
            print_log(str(exc), level=logging.ERROR)
        return 1
    return None


def machine_json(
    command: str,
    *,
    all_result: bool = False,
    result_template: str | None = None,
    supplier_prices: str | None = None,
    config_path: str | None = None,
) -> int:
    """Выполнить команду, JSON в stdout. Логи в этом режиме не печатаются."""
    ensure_services_configured()
    set_print_quiet(True)
    code = _emit_command(
        command,
        all_result,
        result_template,
        config_path if command == LOAD_CONFIG else supplier_prices,
    )
    set_print_quiet(False)
    return code


def _emit_command(
    command: str,
    all_result: bool,
    result_template: str | None,
    payload_arg: str | None,
) -> int:
    started = time.monotonic()
    try:
        emit_json(_command_payload(command, all_result, result_template, payload_arg), started=started)
    except KeyboardInterrupt:
        emit_json(
            error_payload(
                command,
                'KeyboardInterrupt',
                _INTERRUPT,
                compact=command in _COMPACT_ERROR_COMMANDS,
            ),
            started=started,
        )
        return 1
    except Exception as exc:
        emit_json(
            error_payload(
                command,
                type(exc).__name__,
                str(exc),
                compact=command in _COMPACT_ERROR_COMMANDS,
            ),
            started=started,
        )
        return 1
    return 0


def _command_payload(
    command: str,
    all_result: bool,
    result_template: str | None,
    payload_arg: str | None,
) -> Mapping[str, Any]:
    if command == GET_SUPLIERS:
        return all_vendor_supplier_catalog()
    if command == LOAD_SUPPLIER_PRICES:
        return _json_load_prices(payload_arg)
    if command == LOAD_CONFIG:
        return {
            'ok': True,
            'action': LOAD_CONFIG,
            'files': load_config(payload_arg or ''),
        }
    if command == ZAPASKA_LOAD_API_DATA:
        ServiceProvider.resolve(zapaska_service.ZapaskaService).upload_data()
        return {
            'ok': True,
            'action': ZAPASKA_LOAD_API_DATA,
        }
    return {PARSE: _json_parse, DOUBLES: _json_doubles}[command](all_result, result_template)


def _json_load_prices(raw: str | None) -> dict[str, object]:
    mapping = parse_prices_json(raw or '')
    catalog = all_vendor_supplier_catalog()
    return {
        'ok': True,
        'action': LOAD_SUPPLIER_PRICES,
        'files': load_supplier_prices(mapping),
        'suppliers': {key: catalog_entry_for(key, catalog)['sup_title'] for key in mapping},
    }


def _json_parse(all_result: bool, result_template: str | None) -> JsonReport:
    started = time.monotonic()
    parse_result = ServiceProvider.resolve(ParseOrchestrator).parse_all()
    files = ServiceProvider.resolve(PriceReportService).write_prices(
        parse_result.parsed_items,
        result_template,
        as_jsonl=True,
    )
    return report_from_result(PARSE, parse_result, files, time.monotonic() - started, all_result=all_result)


def _json_doubles(all_result: bool, _result_template: str | None) -> JsonReport:
    started = time.monotonic()
    report = ServiceProvider.resolve(doubles_service.DoublesService).make_report(as_jsonl=True)
    return report_from_result(
        DOUBLES,
        report.parse_result,
        jsonl_output_files([report.path]),
        time.monotonic() - started,
        rows=report.doubles,
        all_result=all_result,
    )
