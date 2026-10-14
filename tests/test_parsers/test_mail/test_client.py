"""IMAP-клиент: поиск письма, сохранение прайса и подключение."""

from __future__ import annotations

import imaplib
import re
from datetime import UTC, datetime
from email import message_from_bytes
from email.message import EmailMessage
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from infrastructure.config.mail_credentials import MailCredentials
from parsers.mail import client as mail_client
from parsers.mail.client import FoundPrice, connect, find_latest_price, save_price
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


def _email(
    sender: str,
    subject: str | None,
    filename: str,
    payload: bytes = b'payload',
    *,
    date: str | None = None,
) -> bytes:
    message = EmailMessage()
    message['From'] = sender
    if subject is not None:
        message['Subject'] = subject
    if date is not None:
        message['Date'] = date
    message.set_content('тело')
    message.add_attachment(payload, maintype='application', subtype='octet-stream', filename=filename)
    return message.as_bytes()


_ImapResult = tuple[str, list[Any]]
_MAILBOX_SPECIALS = frozenset('(){ %*"\\')
_QUOTED = re.compile(r'"(.*)"', re.DOTALL)
_BAD: _ImapResult = ('BAD', [b''])
_Args = tuple[Any, ...]
_Messages = dict[bytes, bytes]
_Call = tuple[str, _Args]


def _server_mailbox(arg: str) -> str | None:
    """Имя папки так, как его разберёт сервер: атом или строка в кавычках; иначе None."""
    quoted = _QUOTED.fullmatch(arg)
    if quoted is not None:
        return re.sub(r'\\(.)', r'\1', quoted.group(1))
    if not arg or any(char in _MAILBOX_SPECIALS for char in arg):
        return None
    return arg


class _FakeClient:
    """IMAP-сервер в памяти: папки, письма по UID, ответ LIST и журнал вызовов.

    Аргументы не нормализуются: ``calls`` хранит их как есть, а SELECT, SEARCH и
    FETCH разбираются строго по протоколу — неверные аргументы дают ``BAD``.
    """

    def __init__(
        self,
        folders: dict[str, dict[bytes, bytes]] | None = None,
        *,
        list_status: str = 'OK',
        list_lines: list[bytes] | None = None,
        search_uids: list[bytes] | None = None,
    ) -> None:
        self.folders = {} if folders is None else folders
        self.list_status = list_status
        self.list_lines = list_lines
        self.search_uids = search_uids
        self.selected: str | None = None
        self.selected_folders: list[str] = []
        self.calls: list[_Call] = []

    def list(self, directory: str, pattern: str) -> _ImapResult:
        self.calls.append(('list', (directory, pattern)))
        if self.list_lines is not None:
            return self.list_status, list(self.list_lines)
        lines = [f'(\\HasNoChildren) "." "{name}"'.encode() for name in self.folders]
        return self.list_status, lines

    def select(self, mailbox: str, readonly: bool = False) -> _ImapResult:
        self.calls.append(('select', (mailbox, readonly)))
        name = _server_mailbox(mailbox)
        if name is None or name not in self.folders:
            # RFC 3501: неудачный SELECT снимает выбор и с прежней папки
            self.selected = None
            return 'NO', [b'']
        self.selected = name
        self.selected_folders.append(name)
        return 'OK', [b'']

    def uid(self, command: str, *args: Any) -> _ImapResult:
        self.calls.append(('uid', (command, *args)))
        messages = self.folders.get(self.selected or '', {})
        # imaplib.IMAP4.uid сам приводит команду к верхнему регистру
        if command.upper() == 'SEARCH':
            return _search_response(messages, args, self.search_uids)
        return _fetch_response(messages, args)

    def login(self, _user: str, password: str) -> _ImapResult:
        return 'OK', [b'']

    def logout(self) -> _ImapResult:
        return 'BYE', [b'']


def _search_response(messages: _Messages, args: _Args, uids: list[bytes] | None) -> _ImapResult:
    """Ответ на ``UID SEARCH None FROM sender``: UID писем, где From содержит sender."""
    sender = _search_sender(args)
    if sender is None:
        return _BAD
    if uids is None:
        uids = _uids_from(messages, sender)
    return 'OK', [b' '.join(uids)]


def _search_sender(args: _Args) -> str | None:
    """Отправитель из критериев SEARCH; другие критерии — None."""
    if args[:-1] != (None, 'FROM'):
        return None
    sender = args[-1]
    return sender.lower() if isinstance(sender, str) else None


def _uids_from(messages: _Messages, sender: str) -> list[bytes]:
    found: list[bytes] = []
    for uid, raw in messages.items():
        if sender in _from_header(raw):
            found.append(uid)
    return found


def _fetch_response(messages: _Messages, args: _Args) -> _ImapResult:
    """Ответ на ``UID FETCH uid (RFC822)``; неизвестный UID — мусор без тела."""
    if args[1:] != ('(RFC822)',):
        return _BAD
    if args[0] not in messages:
        return 'OK', [b'garbage']
    return 'OK', [(b'1 (RFC822)', messages[args[0]])]


def _from_header(raw: bytes) -> str:
    return str(message_from_bytes(raw).get('From', '')).lower()


def test_find_latest_price_returns_newest_match() -> None:
    """Из нескольких подходящих писем берётся последнее по UID."""
    fake = _FakeClient(
        {
            'INBOX': {
                b'1': _email('a@b.ru', 'старый прайс', 'price.xlsx'),
                b'2': _email('a@b.ru', 'новый прайс', 'price.xlsx', payload=b'fresh'),
            },
        },
    )
    found = find_latest_price(fake, ['INBOX'], profile=_profile())
    assert found is not None
    assert found.subject == 'новый прайс'
    assert found.payload == b'fresh'
    assert found.filename == 'price.xlsx'


def test_find_latest_price_none_when_no_match() -> None:
    """Если ни одно письмо не подходит, ничего не найдено."""
    fake = _FakeClient({'INBOX': {b'1': _email('other@x.ru', 'прайс', 'price.xlsx')}})
    assert find_latest_price(fake, ['INBOX'], profile=_profile()) is None


def test_find_latest_price_skips_broken_fetch() -> None:
    """Письмо, которое не удалось разобрать, пропускается ради следующего."""
    messages = {b'1': _email('a@b.ru', 'валидный', 'price.xlsx')}
    fake = _FakeClient({'INBOX': messages}, search_uids=[b'1', b'9'])
    found = find_latest_price(fake, ['INBOX'], profile=_profile())
    assert found is not None
    assert found.subject == 'валидный'


def test_find_latest_price_prefers_newest_across_folders() -> None:
    """Более свежее письмо из подпапки важнее старого письма из INBOX."""
    fake = _FakeClient(
        {
            'INBOX': {b'1': _email('a@b.ru', 'старый', 'price.xlsx', date='Mon, 01 Jan 2024 10:00:00 +0300')},
            'INBOX.Prices': {
                b'1': _email(
                    'a@b.ru', 'свежий', 'price.xlsx', payload=b'fresh', date='Tue, 02 Jan 2024 10:00:00 +0300'
                ),
            },
        },
    )
    found = find_latest_price(fake, ['INBOX', 'INBOX.Prices'], profile=_profile())
    assert found is not None
    assert found.subject == 'свежий'


def test_find_latest_price_skips_unselectable_folder() -> None:
    """Недоступная папка пропускается, поиск продолжается в следующей."""
    fake = _FakeClient({'INBOX.Prices': {b'1': _email('a@b.ru', 'прайс', 'price.xlsx')}})
    found = find_latest_price(fake, ['INBOX', 'INBOX.Prices'], profile=_profile())
    assert found is not None
    assert fake.selected_folders == ['INBOX.Prices']


def test_find_latest_price_no_search_in_unselected_folder() -> None:
    """После неудачного SELECT письма в этой папке не ищутся."""
    fake = _FakeClient({'INBOX': {b'1': _email('a@b.ru', 'прайс', 'price.xlsx')}})
    found = find_latest_price(fake, ['INBOX', 'INBOX.Missing'], profile=_profile())
    assert found is not None
    commands = [args[0] for _name, args in fake.calls]
    assert commands.count('SEARCH') == 1
    assert fake.calls[-1] == ('select', ('INBOX.Missing', True))


def test_find_latest_price_quotes_folder_with_space() -> None:
    """Папка с пробелом передаётся в SELECT в кавычках."""
    fake = _FakeClient({'INBOX.My Prices': {b'1': _email('a@b.ru', 'прайс', 'price.xlsx')}})
    found = find_latest_price(fake, ['INBOX.My Prices'], profile=_profile())
    assert found is not None
    assert fake.selected_folders == ['INBOX.My Prices']


def test_list_price_folders_filters_subtree() -> None:
    """Из ответа LIST берутся INBOX и его подпапки, кроме \\Noselect и чужих."""
    lines = [
        b'(\\HasNoChildren) "." "INBOX"',
        b'(\\HasChildren) "." "INBOX.Prices"',
        b'(\\HasNoChildren) "." "INBOX.Prices.2024"',
        b'(\\HasNoChildren) "." "Sent"',
        b'(\\Noselect) "." "INBOX.Container"',
    ]
    fake = _FakeClient({}, list_lines=lines)
    assert mail_client.list_price_folders(fake, 'INBOX') == ['INBOX', 'INBOX.Prices', 'INBOX.Prices.2024']


def test_list_price_folders_adds_root_when_absent() -> None:
    """Если сервер не вернул саму INBOX, она добавляется первой."""
    fake = _FakeClient({}, list_lines=[b'(\\HasNoChildren) "." "INBOX.Prices"'])
    assert mail_client.list_price_folders(fake, 'INBOX') == ['INBOX', 'INBOX.Prices']


def test_list_price_folders_keeps_root_on_error() -> None:
    """Сбой LIST не мешает искать хотя бы в корневой папке."""
    fake = _FakeClient({'INBOX': {}}, list_status='NO')
    assert mail_client.list_price_folders(fake, 'INBOX') == ['INBOX']


def test_list_price_folders_nil_delimiter() -> None:
    """Без разделителя иерархии в поддерево попадает только сам корень."""
    lines = [b'(\\HasNoChildren) NIL "INBOX"', b'(\\HasNoChildren) NIL "Other"']
    fake = _FakeClient({}, list_lines=lines)
    assert mail_client.list_price_folders(fake, 'INBOX') == ['INBOX']


def test_parse_list_entry_ignores_garbage() -> None:
    """Строки, не похожие на LIST, и не-bytes не разбираются."""
    assert mail_client._parse_list_entry(b'garbage') is None
    assert mail_client._parse_list_entry(None) is None


def test_parse_list_entry_unquotes_name() -> None:
    """Кавычки и обратные слэши в имени папки снимаются."""
    parsed = mail_client._parse_list_entry(b'(\\HasNoChildren) "." "INBOX.My \\"Prices\\""')
    assert parsed is not None
    _flags, delimiter, name = parsed
    assert delimiter == '.'
    assert name == 'INBOX.My "Prices"'


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
    fake.select.assert_called_once_with('INBOX', True)


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


def test_find_latest_price_imap_protocol() -> None:
    """SELECT только для чтения с квотингом, SEARCH по FROM и FETCH целого письма."""
    fake = _FakeClient({'INBOX.My Prices': {b'7': _email('a@b.ru', 'прайс', 'price.xlsx')}})
    find_latest_price(fake, ['INBOX.My Prices'], profile=_profile())
    assert fake.calls == [
        ('select', ('"INBOX.My Prices"', True)),
        ('uid', ('SEARCH', None, 'FROM', 'a@b.ru')),
        ('uid', ('FETCH', b'7', '(RFC822)')),
    ]


def test_find_latest_price_keeps_newer_from_first_folder() -> None:
    """Более старое письмо из следующей папки не вытесняет свежее из первой."""
    fake = _FakeClient(
        {
            'INBOX': {b'1': _email('a@b.ru', 'свежий', 'price.xlsx', date='Tue, 02 Jan 2024 10:00:00 +0300')},
            'INBOX.Prices': {b'1': _email('a@b.ru', 'старый', 'price.xlsx', date='Mon, 01 Jan 2024 10:00:00 +0300')},
        },
    )
    found = find_latest_price(fake, ['INBOX', 'INBOX.Prices'], profile=_profile())
    assert found is not None
    assert found.subject == 'свежий'


def test_find_latest_price_sender_domain() -> None:
    """Профиль с доменом отправителя принимает любой адрес этого домена."""
    fake = _FakeClient({'INBOX': {b'1': _email('Price <sales@b.ru>', 'прайс', 'price.xlsx')}})
    found = find_latest_price(fake, ['INBOX'], profile=_profile(sender='b.ru', sender_is_domain=True))
    assert found is not None
    assert found.subject == 'прайс'


def test_find_latest_price_subject_keyword() -> None:
    """Ключевое слово темы отсекает свежее письмо без него — берётся старое с ним."""
    fake = _FakeClient(
        {
            'INBOX': {
                b'1': _email('a@b.ru', 'Прайс шины', 'price.xlsx', payload=b'old'),
                b'2': _email('a@b.ru', 'счёт', 'price.xlsx', payload=b'new'),
            },
        },
    )
    found = find_latest_price(fake, ['INBOX'], profile=_profile(subject_keyword='прайс'))
    assert found is not None
    assert found.payload == b'old'


def test_find_latest_price_message_without_headers() -> None:
    """Письмо без темы и даты: пустая тема, дата неизвестна."""
    fake = _FakeClient({'INBOX': {b'1': _email('a@b.ru', None, 'price.xlsx')}})
    found = find_latest_price(fake, ['INBOX'], profile=_profile())
    assert found == FoundPrice(subject='', date='дата неизвестна', filename='price.xlsx', payload=b'payload')


def test_list_price_folders_requests_all_mailboxes() -> None:
    """LIST запрашивает все папки от корня иерархии."""
    fake = _FakeClient({'INBOX': {}})
    mail_client.list_price_folders(fake, 'INBOX')
    assert fake.calls == [('list', ('""', '*'))]


def test_list_price_folders_root_first() -> None:
    """Корень всегда первым, даже если сервер вернул его после подпапок."""
    lines = [b'(\\HasNoChildren) "." "INBOX.Prices"', b'(\\HasChildren) "." "INBOX"']
    fake = _FakeClient({}, list_lines=lines)
    assert mail_client.list_price_folders(fake, 'INBOX') == ['INBOX', 'INBOX.Prices']


def test_parse_list_entry_lowercase_nil() -> None:
    """NIL — атом IMAP, регистр не важен: разделителя нет."""
    assert mail_client._parse_list_entry(b'(\\HasNoChildren) nil "INBOX"') == (
        frozenset((b'\\HasNoChildren',)),
        None,
        'INBOX',
    )


@pytest.mark.parametrize(
    ('token', 'expected'),
    [
        (b'NIL', None),
        (b'nil', None),
        (b'Nil', None),
        (b'"."', '.'),
        (b'"/"', '/'),
        (b'""', None),
    ],
    ids=['nil-upper', 'nil-lower', 'nil-mixed', 'dot', 'slash', 'empty'],
)
def test_delimiter(token: bytes, expected: str | None) -> None:
    """Разделитель иерархии: NIL в любом регистре и пустая строка — нет разделителя."""
    assert mail_client._delimiter(token) == expected


@pytest.mark.parametrize(
    ('token', 'expected'),
    [
        (b'INBOX', 'INBOX'),
        (b'  "INBOX"  ', 'INBOX'),
        (b'"', '"'),
        (b'""', ''),
        (b'"abc', '"abc'),
        (b'abc"', 'abc"'),
        (b'"a\\"b\\\\c"', 'a"b\\c'),
        (b'"\xff"', '\ufffd'),
    ],
    ids=['atom', 'spaces', 'one-quote', 'empty-quoted', 'open-only', 'close-only', 'escapes', 'bad-utf8'],
)
def test_unquote(token: bytes, expected: str) -> None:
    """Кавычки снимаются только с полной IMAP-строки; битый UTF-8 не роняет разбор."""
    assert mail_client._unquote(token) == expected


@pytest.mark.parametrize(
    ('name', 'expected'),
    [
        ('INBOX', 'INBOX'),
        ('INBOX.Prices', 'INBOX.Prices'),
        ('', '""'),
        ('My Prices', '"My Prices"'),
        ('a\\b"c', '"a\\\\b\\"c"'),
    ],
    ids=['atom', 'dotted', 'empty', 'space', 'escapes'],
)
def test_mailbox_arg(name: str, expected: str) -> None:
    """Атом передаётся как есть; пустое имя и спецсимволы — в кавычках с экранированием."""
    assert mail_client._mailbox_arg(name) == expected


class _StubClient(_FakeClient):
    """Клиент с фиксированным ответом uid."""

    def __init__(self, response: _ImapResult) -> None:
        super().__init__()
        self.response = response

    def uid(self, command: str, *args: Any) -> _ImapResult:
        self.calls.append(('uid', (command, *args)))
        return self.response


@pytest.mark.parametrize(
    ('response', 'expected'),
    [
        (('OK', [b'1 2']), [b'1', b'2']),
        (('NO', [b'1 2']), []),
        (('OK', []), []),
    ],
    ids=['ok', 'bad-status-with-data', 'ok-without-data'],
)
def test_search_uids_status(response: tuple[str, list[Any]], expected: list[bytes]) -> None:
    """UID берутся только из успешного непустого ответа SEARCH."""
    stub = _StubClient(response)
    assert mail_client._search_uids(stub, 'a@b.ru') == expected


@pytest.mark.parametrize(
    'response',
    [('NO', [(b'1 (RFC822)', b'Subject: x\r\n\r\nbody')]), ('OK', [])],
    ids=['bad-status-with-body', 'ok-without-data'],
)
def test_fetch_message_rejects(response: tuple[str, list[Any]]) -> None:
    """Неуспешный или пустой ответ FETCH не даёт письма."""
    assert mail_client._fetch_message(_StubClient(response), b'1') is None


def _found(when: datetime | None) -> FoundPrice:
    return FoundPrice(subject='', date='', filename='price.xlsx', payload=b'', when=when)


_EARLY = datetime(2024, 1, 1, tzinfo=UTC)
_LATE = datetime(2024, 1, 2, tzinfo=UTC)


@pytest.mark.parametrize(
    ('best_when', 'candidate_when', 'expect_candidate'),
    [
        (_EARLY, _LATE, True),
        (_LATE, _EARLY, False),
        (_EARLY, _EARLY, False),
        (None, _EARLY, True),
        (_EARLY, None, False),
    ],
    ids=['newer', 'older', 'equal', 'best-undated', 'candidate-undated'],
)
def test_newer_of(best_when: datetime | None, candidate_when: datetime | None, expect_candidate: bool) -> None:
    """Кандидат вытесняет лучшее только строго более свежей датой; без даты — самое старое."""
    best, candidate = _found(best_when), _found(candidate_when)
    assert (mail_client._newer_of(best, candidate) is candidate) is expect_candidate


def test_newer_of_missing() -> None:
    """Отсутствующее письмо с любой стороны не вытесняет имеющееся."""
    found = _found(_EARLY)
    assert mail_client._newer_of(None, found) is found
    assert mail_client._newer_of(found, None) is found
    assert mail_client._newer_of(None, None) is None


def test_save_price_creates_nested_folder(tmp_path: Path) -> None:
    """Прайс пишется в несуществующую вложенную папку, повторная запись перезаписывает."""
    dest = tmp_path / 'file_prices' / 'pioner' / 'price.xlsx'
    save_price(dest, b'first')
    save_price(dest, b'second')
    assert dest.read_bytes() == b'second'
    assert sorted(path.name for path in dest.parent.iterdir()) == ['price.xlsx']


def test_connect_quotes_folder(monkeypatch: pytest.MonkeyPatch) -> None:
    """Папка со спецсимволами открывается в кавычках, как и при поиске."""
    fake = _FakeClient({'INBOX.My Prices': {}})
    monkeypatch.setattr(mail_client, 'open_client', lambda account: fake)
    account = MailAccount(host='imap.example.ru', port=993, folder='INBOX.My Prices')

    assert connect(account, _CREDENTIALS) is fake
    assert fake.calls == [('select', ('"INBOX.My Prices"', True))]
