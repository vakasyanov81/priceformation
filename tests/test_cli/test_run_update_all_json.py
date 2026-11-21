"""JSON-режим обновления всех поставщиков: API и почта, ответ по каждому источнику."""

import json
from unittest.mock import MagicMock, patch

import pytest

from app.run_argv import UPDATE_ALL_SUPPLIER_PRICES
from app.run_machine import machine_json
from domain.exceptions import CoreExceptionError
from services.four_tochki_service import FourTochkiService
from services.mail_results import MailFetchReport, MailFetchResult
from services.mail_service import MailService
from services.mim_service import MimService
from services.price_schema_service import PriceSchemaService
from services.zapaska_service import ZapaskaService

_RESOLVE = 'app.run_machine.ServiceProvider.resolve'
_MAIL_FILE = 'file_prices/stk/price.xlsx'
_Services = dict[type, MagicMock]
_Capsys = pytest.CaptureFixture[str]


def _services(
    *,
    zapaska_error: Exception | None = None,
    mail_error: Exception | None = None,
) -> _Services:
    zapaska = MagicMock()
    zapaska.upload_data.side_effect = zapaska_error
    mail = MagicMock()
    mail.fetch_report.side_effect = mail_error
    mail.fetch_report.return_value = MailFetchReport(
        [MailFetchResult('stk', 'Прайс', '', 'price.xlsx', _MAIL_FILE)],
        {'stk': 'ok', 'mim': 'skipped'},
    )
    return {
        ZapaskaService: zapaska,
        FourTochkiService: MagicMock(),
        MimService: MagicMock(),
        MailService: mail,
        PriceSchemaService: MagicMock(),
    }


def _run(services: _Services, capsys: _Capsys) -> dict[str, object]:
    with patch(_RESOLVE, side_effect=services.__getitem__):
        machine_json(UPDATE_ALL_SUPPLIER_PRICES)
    payload: dict[str, object] = json.loads(capsys.readouterr().out)
    return payload


def test_all_sources_ok(capsys: _Capsys) -> None:
    """все источники отработали: ok, пустой errors, файлы из почты."""
    services = _services()
    payload = _run(services, capsys)
    assert payload['ok'] is True
    assert payload['action'] == UPDATE_ALL_SUPPLIER_PRICES
    assert payload['sources'] == {
        'zapaska': {'status': 'ok', 'source': 'api'},
        'four_tochki': {'status': 'ok', 'source': 'api'},
        'mim': {'status': 'ok', 'source': 'api'},
        'stk': {'status': 'ok', 'source': 'email'},
    }
    assert payload['errors'] == {}
    assert payload['files'] == [_MAIL_FILE]
    services[FourTochkiService].upload_data.assert_called_once_with()
    services[MimService].upload_data.assert_called_once_with()


def test_api_failure_does_not_stop_mail(capsys: _Capsys) -> None:
    """ошибка запаски попадает в errors, остальные источники всё равно выполняются."""
    services = _services(zapaska_error=CoreExceptionError('нет связи с API'))
    payload = _run(services, capsys)
    assert payload['ok'] is False
    assert payload['sources'] == {
        'zapaska': {'status': 'error', 'source': 'api'},
        'four_tochki': {'status': 'ok', 'source': 'api'},
        'mim': {'status': 'ok', 'source': 'api'},
        'stk': {'status': 'ok', 'source': 'email'},
    }
    assert payload['errors'] == {'zapaska': 'нет связи с API'}
    assert payload['files'] == [_MAIL_FILE]
    services[FourTochkiService].upload_data.assert_called_once_with()
    services[MailService].fetch_report.assert_called_once_with()


def test_mail_failure_is_reported_without_files(capsys: _Capsys) -> None:
    """ошибка почты: errors.mail, files пуст, API уже выгружены."""
    services = _services(mail_error=CoreExceptionError('нет доступа к ящику'))
    payload = _run(services, capsys)
    assert payload['ok'] is False
    assert payload['sources'] == {
        'zapaska': {'status': 'ok', 'source': 'api'},
        'four_tochki': {'status': 'ok', 'source': 'api'},
        'mim': {'status': 'ok', 'source': 'api'},
    }
    assert payload['errors'] == {'mail': 'нет доступа к ящику'}
    assert payload['files'] == []
    services[ZapaskaService].upload_data.assert_called_once_with()


def test_disabled_api_source_is_skipped(capsys: _Capsys) -> None:
    """Отключённый поставщик получает статус skipped в отчёте по источникам."""
    services = _services()
    services[ZapaskaService].upload_data.return_value = False
    services[MimService].upload_data.return_value = False
    payload = _run(services, capsys)
    assert payload['ok'] is True
    assert payload['sources'] == {
        'zapaska': {'status': 'skipped', 'source': 'api'},
        'four_tochki': {'status': 'ok', 'source': 'api'},
        'mim': {'status': 'skipped', 'source': 'email'},
        'stk': {'status': 'ok', 'source': 'email'},
    }
    assert payload['errors'] == {}
    assert payload['files'] == [_MAIL_FILE]
