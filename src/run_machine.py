"""JSON-режим CLI: разбор прайса и ответ в stdout."""

import logging
import time
from collections.abc import Mapping
from typing import Any

from domain.exceptions import ConfigValidationError
from infrastructure.logging.json_mode import quiet_console
from parse_report import JsonReport, emit_json, error_payload
from parse_report_build import report_from_result
from parsers.all_vendors import all_vendor_supplier_catalog
from parsers.common_price_output import jsonl_output_files
from parsers.load_config import load_config
from parsers.load_supplier_prices import catalog_entry_for, load_supplier_prices, parse_prices_json
from parsers.strategies.product_types import CANONICAL_TYPES
from parsers.writer.templates.all_templates import UnknownWriterTemplateError, get_writer_template
from run_argv import (
    DOUBLES,
    FETCH_MAIL_PRICES,
    FOUR_TOCHKI_LOAD_API_DATA,
    GET_PRODUCT_TYPES,
    GET_SUPLIERS,
    GET_VENDORS,
    LOAD_CONFIG,
    LOAD_SUPPLIER_PRICES,
    MIM_LOAD_API_DATA,
    PARSE,
    TOGGLE_VENDOR,
    ZAPASKA_LOAD_API_DATA,
)
from services import doubles_service, four_tochki_service, zapaska_service
from services.configure import ensure_services_configured
from services.mail_service import MailService
from services.mim_service import MimService
from services.parse_orchestrator import ParseOrchestrator
from services.price_report import PriceReportService
from services.service_provider import ServiceProvider
from services.vendor_activation import VendorActivationService, VendorState

logger = logging.getLogger(__name__)

_INTERRUPT = 'interrupted'
_JSON_OK = 'ok'
_JSON_ACTION = 'action'
_DOWNLOAD_COMMANDS = frozenset((ZAPASKA_LOAD_API_DATA, FOUR_TOCHKI_LOAD_API_DATA, MIM_LOAD_API_DATA, FETCH_MAIL_PRICES))
_COMPACT_ERROR_COMMANDS = frozenset(
    (
        LOAD_SUPPLIER_PRICES,
        LOAD_CONFIG,
        ZAPASKA_LOAD_API_DATA,
        FOUR_TOCHKI_LOAD_API_DATA,
        MIM_LOAD_API_DATA,
        FETCH_MAIL_PRICES,
        GET_VENDORS,
        TOGGLE_VENDOR,
    ),
)


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
            logger.error(str(exc))
        return 1
    return None


def machine_json(
    command: str,
    *,
    all_result: bool = False,
    result_template: str | None = None,
    supplier_prices: str | None = None,
    config_path: str | None = None,
    vendor_folder: str | None = None,
) -> int:
    """Выполнить команду, JSON в stdout. Логи в этом режиме не печатаются."""
    ensure_services_configured()
    payload_args = {LOAD_CONFIG: config_path, TOGGLE_VENDOR: vendor_folder}
    with quiet_console():
        return _emit_command(command, all_result, result_template, payload_args.get(command, supplier_prices))


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
    reference = _reference_payload(command, payload_arg)
    if reference is not None:
        return reference
    if command == LOAD_SUPPLIER_PRICES:
        return _json_load_prices(payload_arg)
    if command == LOAD_CONFIG:
        return {
            _JSON_OK: True,
            _JSON_ACTION: LOAD_CONFIG,
            'files': load_config(payload_arg or ''),
        }
    if command in _DOWNLOAD_COMMANDS:
        return _json_download(command)
    return {PARSE: _json_parse, DOUBLES: _json_doubles}[command](all_result, result_template)


def _reference_payload(command: str, payload_arg: str | None) -> Mapping[str, Any] | None:
    """Справочные команды: каталог поставщиков, типы товара и активность поставщиков; None — команда не справочная."""
    if command == GET_SUPLIERS:
        return all_vendor_supplier_catalog()
    if command == GET_PRODUCT_TYPES:
        return {_JSON_OK: True, _JSON_ACTION: GET_PRODUCT_TYPES, 'types': list(CANONICAL_TYPES)}
    if command == GET_VENDORS:
        return _vendors_payload()
    if command == TOGGLE_VENDOR:
        return _toggle_vendor_payload(payload_arg)
    return None


def _vendors_payload() -> Mapping[str, Any]:
    """Поставщики (файлы конфигов) с признаком активности: как в интерактивном меню."""
    states = ServiceProvider.resolve(VendorActivationService).list_vendors()
    return {_JSON_OK: True, _JSON_ACTION: GET_VENDORS, 'vendors': [_vendor_json(state) for state in states]}


def _toggle_vendor_payload(folder: str | None) -> Mapping[str, Any]:
    """Переключить активность поставщика по папке; неизвестная папка — ошибка, файл не меняется."""
    service = ServiceProvider.resolve(VendorActivationService)
    known = {state.folder for state in service.list_vendors()}
    if folder not in known:
        raise ConfigValidationError(f'неизвестный поставщик: {folder}')
    return {_JSON_OK: True, _JSON_ACTION: TOGGLE_VENDOR, 'vendor': _vendor_json(service.toggle(folder))}


def _vendor_json(state: VendorState) -> dict[str, Any]:
    return {'folder': state.folder, 'name': state.name, 'enabled': state.enabled}


def _json_download(command: str) -> Mapping[str, Any]:
    """Выгрузить удалённые прайсы (API запаски / Форточек / МИМ или почта) и вернуть ответ."""
    if command == ZAPASKA_LOAD_API_DATA:
        ServiceProvider.resolve(zapaska_service.ZapaskaService).upload_data()
        return {_JSON_OK: True, _JSON_ACTION: ZAPASKA_LOAD_API_DATA}
    if command == FOUR_TOCHKI_LOAD_API_DATA:
        upload_four_tochki_data()
        return {_JSON_OK: True, _JSON_ACTION: FOUR_TOCHKI_LOAD_API_DATA}
    if command == MIM_LOAD_API_DATA:
        ServiceProvider.resolve(MimService).upload_data()
        return {_JSON_OK: True, _JSON_ACTION: MIM_LOAD_API_DATA}
    fetched = ServiceProvider.resolve(MailService).fetch_prices()
    return {
        _JSON_OK: True,
        _JSON_ACTION: FETCH_MAIL_PRICES,
        'files': [entry.path for entry in fetched],
    }


def upload_four_tochki_data() -> None:
    """Выгрузить данные Форточек по API в file_prices/four_tochki."""
    ServiceProvider.resolve(four_tochki_service.FourTochkiService).upload_data()


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
        template=result_template,
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
