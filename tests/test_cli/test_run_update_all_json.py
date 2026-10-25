"""JSON-режим обновления всех поставщиков: API и почта, ответ по каждому источнику."""

import contextlib
import json
import types
from unittest.mock import MagicMock, patch

import pytest

from domain.exceptions import CoreExceptionError
from run_argv import UPDATE_ALL_SUPPLIER_PRICES
from run_machine import machine_json
from services.four_tochki_service import FourTochkiService
from services.mail_service import MailService
from services.mim_service import MimService
from services.zapaska_service import ZapaskaService

_RESOLVE = 'run_machine.ServiceProvider.resolve'
_SCHEMA_GUARD = 'run_machine.schema_guard'
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
    mail.fetch_prices.side_effect = mail_error
    mail.fetch_prices.return_value = [types.SimpleNamespace(path=_MAIL_FILE)]
    return {
        ZapaskaService: zapaska,
        FourTochkiService: MagicMock(),
        MimService: MagicMock(),
        MailService: mail,
    }


def _run(services: _Services, capsys: _Capsys) -> dict[str, object]:
    with (
        patch(_RESOLVE, side_effect=services.__getitem__),
        patch(_SCHEMA_GUARD, return_value=contextlib.nullcontext()),
    ):
        machine_json(UPDATE_ALL_SUPPLIER_PRICES)
    payload: dict[str, object] = json.loads(capsys.readouterr().out)
    return payload


def test_all_sources_ok(capsys: _Capsys) -> None:
    """все источники отработали: ok, пустой errors, файлы из почты."""
    services = _services()
    payload = _run(services, capsys)
    assert payload['ok'] is True
    assert payload['action'] == UPDATE_ALL_SUPPLIER_PRICES
    assert payload['sources'] == {'zapaska': 'ok', 'four_tochki': 'ok', 'mim': 'ok', 'mail': 'ok'}
    assert payload['errors'] == {}
    assert payload['files'] == [_MAIL_FILE]
    services[FourTochkiService].upload_data.assert_called_once_with()
    services[MimService].upload_data.assert_called_once_with()


def test_api_failure_does_not_stop_mail(capsys: _Capsys) -> None:
    """ошибка запаски попадает в errors, остальные источники всё равно выполняются."""
    services = _services(zapaska_error=CoreExceptionError('нет связи с API'))
    payload = _run(services, capsys)
    assert payload['ok'] is False
    assert payload['sources'] == {'zapaska': 'error', 'four_tochki': 'ok', 'mim': 'ok', 'mail': 'ok'}
    assert payload['errors'] == {'zapaska': 'нет связи с API'}
    assert payload['files'] == [_MAIL_FILE]
    services[FourTochkiService].upload_data.assert_called_once_with()
    services[MailService].fetch_prices.assert_called_once_with()


def test_mail_failure_is_reported_without_files(capsys: _Capsys) -> None:
    """ошибка почты: errors.mail, files пуст, API уже выгружены."""
    services = _services(mail_error=CoreExceptionError('нет доступа к ящику'))
    payload = _run(services, capsys)
    assert payload['ok'] is False
    assert payload['sources'] == {'zapaska': 'ok', 'four_tochki': 'ok', 'mim': 'ok', 'mail': 'error'}
    assert payload['errors'] == {'mail': 'нет доступа к ящику'}
    assert payload['files'] == []
    services[ZapaskaService].upload_data.assert_called_once_with()
