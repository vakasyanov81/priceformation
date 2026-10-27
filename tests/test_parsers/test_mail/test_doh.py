"""Подключение к IMAP: SSL, запасное разрешение имени через DoH и сокет по адресу."""

from __future__ import annotations

import imaplib
import io
import json
import logging
import socket
import ssl
import urllib.request
from typing import Any
from unittest.mock import MagicMock, call

import pytest
from log_watch import LoggerWatcher

from parsers.mail import doh as mail_doh
from parsers.mail.doh import _ImapSslByAddress
from parsers.mail.errors import MailConnectionError
from parsers.mail.models import MailAccount

_ACCOUNT = MailAccount(host='imap.example.ru', port=993, folder='INBOX')


@pytest.fixture
def ssl_context(monkeypatch: pytest.MonkeyPatch) -> object:
    """Контекст SSL, который вернёт ssl.create_default_context."""
    context = object()
    monkeypatch.setattr(ssl, 'create_default_context', lambda: context)
    return context


def test_open_client_system_dns(monkeypatch: pytest.MonkeyPatch, ssl_context: object) -> None:
    """Системный DNS: IMAP4_SSL с хостом, портом, контекстом и таймаутом."""
    imap_ssl = MagicMock()
    monkeypatch.setattr(imaplib, 'IMAP4_SSL', imap_ssl)

    assert mail_doh.open_client(_ACCOUNT) is imap_ssl.return_value
    imap_ssl.assert_called_once_with('imap.example.ru', 993, ssl_context=ssl_context, timeout=30)


def test_open_client_doh_fallback(monkeypatch: pytest.MonkeyPatch, ssl_context: object) -> None:
    """Сбой системного DNS переводит открытие на DoH с тем же контекстом SSL."""
    monkeypatch.setattr(imaplib, 'IMAP4_SSL', MagicMock(side_effect=socket.gaierror))
    via_doh = MagicMock()
    monkeypatch.setattr(mail_doh, '_open_client_via_doh', via_doh)

    assert mail_doh.open_client(_ACCOUNT) is via_doh.return_value
    via_doh.assert_called_once_with(_ACCOUNT, ssl_context)


def test_open_client_via_doh_unresolved(monkeypatch: pytest.MonkeyPatch) -> None:
    """DoH не дал адресов — ошибка с именем хоста."""
    doh_addresses = MagicMock(return_value=[])
    monkeypatch.setattr(mail_doh, '_doh_addresses', doh_addresses)

    with pytest.raises(MailConnectionError) as error:
        mail_doh._open_client_via_doh(_ACCOUNT, MagicMock())

    assert str(error.value) == "Не удалось разрешить 'imap.example.ru' ни системным DNS, ни через DoH."
    doh_addresses.assert_called_once_with('imap.example.ru')


def test_open_client_via_doh_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Первый адрес из DoH: подключение с хостом, портом, адресом, контекстом и таймаутом."""
    context = MagicMock()
    by_address = MagicMock()
    monkeypatch.setattr(mail_doh, '_doh_addresses', lambda host: ['1.2.3.4', '5.6.7.8'] if host else [])
    monkeypatch.setattr(mail_doh, '_ImapSslByAddress', by_address)

    assert mail_doh._open_client_via_doh(_ACCOUNT, context) is by_address.return_value
    by_address.assert_called_once_with('imap.example.ru', 993, '1.2.3.4', context, 30)


def test_open_client_via_doh_all_fail(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ни один адрес не подошёл — ошибка с host:port и причиной по каждому адресу."""
    context = MagicMock()
    by_address = MagicMock(side_effect=[OSError('refused'), ssl.SSLError('handshake')])
    monkeypatch.setattr(mail_doh, '_doh_addresses', lambda host: ['1.2.3.4', '5.6.7.8'])
    monkeypatch.setattr(mail_doh, '_ImapSslByAddress', by_address)

    with pytest.raises(MailConnectionError) as error:
        mail_doh._open_client_via_doh(_ACCOUNT, context)

    reasons = "1.2.3.4: OSError('refused'); 5.6.7.8: SSLError('handshake')"
    assert str(error.value) == f'Не удалось подключиться к imap.example.ru:993 ({reasons})'
    assert by_address.call_args_list == [
        call('imap.example.ru', 993, '1.2.3.4', context, 30),
        call('imap.example.ru', 993, '5.6.7.8', context, 30),
    ]


def test_doh_addresses_request(monkeypatch: pytest.MonkeyPatch) -> None:
    """Запрос к Cloudflare: URL с хостом, заголовок Accept и таймаут."""
    payload = {'Answer': [{'type': 1, 'data': '10.0.0.1'}]}
    urlopen = _patch_urlopen(monkeypatch, [_json_response(payload)])

    assert mail_doh._doh_addresses('imap.example.ru') == ['10.0.0.1']
    (request,), kwargs = urlopen.call_args
    assert request.full_url == 'https://cloudflare-dns.com/dns-query?name=imap.example.ru&type=A'
    assert request.headers == {'Accept': 'application/dns-json'}
    assert kwargs == {'timeout': 10}


def test_doh_addresses_fallback_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    """Сбой первого провайдера переводит запрос на Google."""
    payload = {'Answer': [{'type': 1, 'data': '10.0.0.2'}]}
    urlopen = _patch_urlopen(monkeypatch, [OSError('cloudflare down'), _json_response(payload)])

    assert mail_doh._doh_addresses('imap.example.ru') == ['10.0.0.2']
    request = urlopen.call_args.args[0]
    assert request.full_url == 'https://dns.google/resolve?name=imap.example.ru&type=A'


def test_doh_addresses_empty_answer_tries_next(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ответ без адресов не останавливает перебор провайдеров."""
    payload = {'Answer': [{'type': 1, 'data': '10.0.0.3'}]}
    _patch_urlopen(monkeypatch, [_json_response({}), _json_response(payload)])
    assert mail_doh._doh_addresses('imap.example.ru') == ['10.0.0.3']


def test_doh_addresses_both_fail(monkeypatch: pytest.MonkeyPatch) -> None:
    """Если DoH недоступен и ответ не JSON — адресов нет."""
    _patch_urlopen(monkeypatch, [io.BytesIO(b'{'), OSError('google down')])
    assert not mail_doh._doh_addresses('imap.example.ru')


def test_doh_answers_filters_entries() -> None:
    """Из ответа DoH берутся только строковые IPv4-адреса."""
    payload = {
        'Answer': [
            {'type': 1, 'data': '10.0.0.1'},
            {'type': 5, 'data': 'alias'},
            {'type': 1, 'data': 123},
            'garbage',
        ],
    }
    assert mail_doh._doh_answers(payload) == ['10.0.0.1']


_NO_ANSWERS: tuple[object, ...] = ([], {}, {'Status': 3})


@pytest.mark.parametrize('payload', _NO_ANSWERS, ids=['not-mapping', 'empty', 'no-answer'])
def test_doh_answers_without_answer(payload: object) -> None:
    """Не объект или объект без Answer — пустой список адресов."""
    assert not mail_doh._doh_answers(payload)


def test_imap_ssl_by_address_uses_expected_socket(monkeypatch: pytest.MonkeyPatch) -> None:
    """_create_socket соединяется по заранее разрешённому адресу с SNI хоста."""
    client = object.__new__(_ImapSslByAddress)
    client._address = '1.2.3.4'
    client.port = 993
    client.host = 'imap.example.ru'
    ssl_context = MagicMock()
    client._ssl_context = ssl_context
    create_connection = MagicMock(return_value='raw')
    monkeypatch.setattr(socket, 'create_connection', create_connection)

    assert client._create_socket(5.0) is ssl_context.wrap_socket.return_value
    create_connection.assert_called_once_with(('1.2.3.4', 993), 5.0)
    ssl_context.wrap_socket.assert_called_once_with('raw', server_hostname='imap.example.ru')


def test_imap_ssl_by_address_rejects_non_blocking() -> None:
    """timeout=0 (неблокирующий сокет) не поддерживается — текст как в imaplib."""
    client = object.__new__(_ImapSslByAddress)
    with pytest.raises(ValueError, match=r'^Non-blocking socket \(timeout=0\) is not supported$'):
        client._create_socket(0)


def _json_response(payload: object) -> io.BytesIO:
    return io.BytesIO(json.dumps(payload).encode())


def _patch_urlopen(monkeypatch: pytest.MonkeyPatch, responses: list[Any]) -> MagicMock:
    urlopen = MagicMock(side_effect=responses)
    monkeypatch.setattr(urllib.request, 'urlopen', urlopen)
    return urlopen


def test_doh_addresses_logs_failed_providers(monkeypatch: pytest.MonkeyPatch, watch_logger: LoggerWatcher) -> None:
    """Сбой каждого DoH-провайдера попадает в лог, а не пропускается молча."""
    entries = watch_logger('parsers.mail.doh')
    _patch_urlopen(monkeypatch, [io.BytesIO(b'{'), OSError('google down')])

    assert not mail_doh._doh_addresses('imap.example.ru')

    texts = [text for level, text in entries() if level == logging.WARNING]
    assert len(texts) == 2
    assert 'cloudflare-dns.com' in texts[0]
    assert 'google down' in texts[1]
