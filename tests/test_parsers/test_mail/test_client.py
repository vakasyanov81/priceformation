"""IMAP-клиент: поиск письма, сохранение прайса, подключение и DoH."""

import imaplib
import io
import json
import socket
import urllib.request
from email.message import EmailMessage
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from infrastructure.config.mail_credentials import MailCredentials
from parsers.mail import client as mail_client
from parsers.mail import doh as mail_doh
from parsers.mail.client import connect, find_latest_price, save_price
from parsers.mail.doh import _ImapSslByAddress
from parsers.mail.errors import MailConnectionError
from parsers.mail.models import MailAccount, MailProfile

_ACCOUNT = MailAccount(host='imap.example.ru', port=993, folder='INBOX')
_CREDENTIALS = MailCredentials(login='user', password='secret')


def _profile(**overrides: Any) -> MailProfile:
    base: dict[str, Any] = {
        'sender': 'a@b.ru',
        'sender_is_domain': False,
        'subject_keyword': None,
        'attachment_glob': '*.xlsx',
        'enabled': True,
    }
    base.update(overrides)
    return MailProfile(**base)


def _email(sender: str, subject: str, filename: str, payload: bytes = b'payload') -> bytes:
    message = EmailMessage()
    message['From'] = sender
    message['Subject'] = subject
    message.set_content('тело')
    message.add_attachment(payload, maintype='application', subtype='octet-stream', filename=filename)
    return message.as_bytes()


class _FakeClient:
    """IMAP-клиент с заранее заданными письмами по UID."""

    def __init__(
        self,
        messages: dict[bytes, bytes],
        *,
        search_status: str = 'OK',
        search_uids: list[bytes] | None = None,
    ) -> None:
        self.messages = messages
        self.search_status = search_status
        self.search_uids = search_uids
        self.logged_out = False

    def uid(self, command: str, *args: Any) -> tuple[str, list[Any]]:
        if command == 'SEARCH':
            uids = self.search_uids
            if uids is None:
                uids = list(self.messages)
            return self.search_status, [b' '.join(uids)]
        if args[0] not in self.messages:
            return 'OK', [b'garbage']
        return 'OK', [(b'1 (RFC822)', self.messages[args[0]])]

    def login(self, _user: str, password: str) -> tuple[str, list[Any]]:
        return 'OK', [b'']

    def select(self, _mailbox: str, _readonly: bool = False) -> tuple[str, list[Any]]:
        return 'OK', [b'']

    def logout(self) -> tuple[str, list[Any]]:
        self.logged_out = True
        return 'BYE', [b'']


def test_find_latest_price_returns_newest_match() -> None:
    """Из нескольких подходящих писем берётся последнее по UID."""
    fake = _FakeClient(
        {
            b'1': _email('a@b.ru', 'старый прайс', 'price.xlsx'),
            b'2': _email('a@b.ru', 'новый прайс', 'price.xlsx', payload=b'fresh'),
        },
    )
    found = find_latest_price(fake, profile=_profile())
    assert found is not None
    assert found.subject == 'новый прайс'
    assert found.payload == b'fresh'
    assert found.filename == 'price.xlsx'


def test_find_latest_price_none_when_no_match() -> None:
    """Если ни одно письмо не подходит, ничего не найдено."""
    fake = _FakeClient({b'1': _email('other@x.ru', 'прайс', 'price.xlsx')})
    assert find_latest_price(fake, profile=_profile()) is None


def test_find_latest_price_skips_broken_fetch() -> None:
    """Письмо, которое не удалось разобрать, пропускается ради следующего."""
    messages = {b'1': _email('a@b.ru', 'валидный', 'price.xlsx')}
    fake = _FakeClient(messages, search_uids=[b'1', b'9'])
    found = find_latest_price(fake, profile=_profile())
    assert found is not None
    assert found.subject == 'валидный'


def test_search_uids_bad_status() -> None:
    """Неуспешный SEARCH не даёт UID."""
    fake = _FakeClient({}, search_status='NO')
    assert not mail_client._search_uids(fake, 'a@b.ru')


def test_search_uids_non_bytes_response() -> None:
    """Ответ SEARCH без bytes не считается списком UID."""
    fake = MagicMock()
    fake.uid.return_value = ('OK', ['not-bytes'])
    assert not mail_client._search_uids(fake, 'a@b.ru')


def test_save_price_writes_and_removes_stale(tmp_path: Path) -> None:
    """Прайс пишется как price.xlsx, устаревший price.xls удаляется."""
    stale = tmp_path / 'price.xls'
    stale.write_bytes(b'old')
    dest = tmp_path / 'price.xlsx'
    save_price(dest, b'new')
    assert dest.read_bytes() == b'new'
    assert not stale.exists()
    assert not (tmp_path / 'price.xlsx.tmp').exists()


def test_connect_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    """connect логинится и открывает папку только для чтения."""
    fake = MagicMock()
    fake.login.return_value = ('OK', [b''])
    fake.select.return_value = ('OK', [b''])
    monkeypatch.setattr(imaplib, 'IMAP4_SSL', MagicMock(return_value=fake))

    client = connect(_ACCOUNT, _CREDENTIALS)

    assert client is fake
    fake.login.assert_called_once_with('user', 'secret')
    fake.select.assert_called_once_with('INBOX', readonly=True)


def test_connect_login_error_logs_out(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ошибка входа разлогинивает клиента и пробрасывается."""
    fake = MagicMock()
    fake.login.side_effect = imaplib.IMAP4.error('bad credentials')
    monkeypatch.setattr(imaplib, 'IMAP4_SSL', MagicMock(return_value=fake))

    with pytest.raises(imaplib.IMAP4.error):
        connect(_ACCOUNT, _CREDENTIALS)

    fake.logout.assert_called_once()


def test_connect_folder_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Недоступная папка — MailConnectionError и logout."""
    fake = MagicMock()
    fake.login.return_value = ('OK', [b''])
    fake.select.return_value = ('NO', [b''])
    monkeypatch.setattr(imaplib, 'IMAP4_SSL', MagicMock(return_value=fake))

    with pytest.raises(MailConnectionError, match='INBOX'):
        connect(_ACCOUNT, _CREDENTIALS)

    fake.logout.assert_called_once()


def test_open_client_doh_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    """Сбой системного DNS переводит открытие на адреса из DoH."""
    monkeypatch.setattr(imaplib, 'IMAP4_SSL', MagicMock(side_effect=socket.gaierror))
    monkeypatch.setattr(mail_doh, '_doh_addresses', lambda host: [])
    with pytest.raises(MailConnectionError, match='разрешить'):
        mail_doh.open_client(_ACCOUNT)


def test_open_client_via_doh_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Первый разрешённый адрес из DoH используется для подключения."""
    sentinel = MagicMock()
    monkeypatch.setattr(mail_doh, '_doh_addresses', lambda host: ['1.2.3.4'])
    monkeypatch.setattr(mail_doh, '_ImapSslByAddress', MagicMock(return_value=sentinel))

    assert mail_doh._open_client_via_doh(_ACCOUNT, MagicMock()) is sentinel


def test_open_client_via_doh_all_fail(monkeypatch: pytest.MonkeyPatch) -> None:
    """Если ни один адрес из DoH не подошёл — MailConnectionError."""
    monkeypatch.setattr(mail_doh, '_doh_addresses', lambda host: ['1.2.3.4', '5.6.7.8'])
    monkeypatch.setattr(mail_doh, '_ImapSslByAddress', MagicMock(side_effect=OSError('refused')))

    with pytest.raises(MailConnectionError, match='подключиться'):
        mail_doh._open_client_via_doh(_ACCOUNT, MagicMock())


def test_doh_addresses_first_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    """Первый успешный провайдер DoH отдаёт адреса."""
    payload = {'Answer': [{'type': 1, 'data': '10.0.0.1'}]}
    _patch_urlopen(monkeypatch, [io.BytesIO(json.dumps(payload).encode())])
    assert mail_doh._doh_addresses('imap.example.ru') == ['10.0.0.1']


def test_doh_addresses_fallback_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    """Сбой первого провайдера переводит запрос на второй."""
    payload = {'Answer': [{'type': 1, 'data': '10.0.0.2'}]}
    response = io.BytesIO(json.dumps(payload).encode())
    _patch_urlopen(monkeypatch, [OSError('cloudflare down'), response])
    assert mail_doh._doh_addresses('imap.example.ru') == ['10.0.0.2']


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


def test_doh_answers_non_mapping() -> None:
    """Не объект — пустой список адресов."""
    assert not mail_doh._doh_answers([])


def test_imap_ssl_by_address_uses_expected_socket(monkeypatch: pytest.MonkeyPatch) -> None:
    """_create_socket соединяется по заранее разрешённому адресу с SNI хоста."""
    client = object.__new__(_ImapSslByAddress)
    client._address = '1.2.3.4'
    client.port = 993
    client.host = 'imap.example.ru'
    ssl_context = MagicMock()
    wrapped = MagicMock()
    ssl_context.wrap_socket.return_value = wrapped
    client._ssl_context = ssl_context
    monkeypatch.setattr(socket, 'create_connection', MagicMock(return_value='raw'))

    assert client._create_socket(5.0) is wrapped
    ssl_context.wrap_socket.assert_called_once_with('raw', server_hostname='imap.example.ru')


def test_imap_ssl_by_address_rejects_non_blocking() -> None:
    """timeout=0 (неблокирующий сокет) не поддерживается."""
    client = object.__new__(_ImapSslByAddress)
    with pytest.raises(ValueError, match='Non-blocking'):
        client._create_socket(0)


def _patch_urlopen(monkeypatch: pytest.MonkeyPatch, responses: list[Any]) -> None:
    monkeypatch.setattr(urllib.request, 'urlopen', MagicMock(side_effect=responses))
