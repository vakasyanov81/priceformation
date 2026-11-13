"""Разбор письма: заголовки, дата, вложения, отправитель."""

import json
from email import message_from_bytes, message_from_string
from email.message import EmailMessage, Message
from pathlib import Path

import pytest

from parsers.mail.body import message_text
from parsers.mail.message import (
    attachment_content,
    decode_header_value,
    matching_attachments,
    message_body,
    sender_matches,
    subject_matches,
)
from parsers.mail.models import MailConfig

_ENCODED_PRICE = '=?utf-8?B?0L/RgNCw0LnRgQ==?='  # «прайс»


def _message(raw: str) -> Message:
    return message_from_string(raw)


def _multipart(sender: str, subject: str, filename: str, payload: bytes) -> Message:
    message = EmailMessage()
    message['From'] = sender
    message['Subject'] = subject
    message.set_content('тело')
    message.add_attachment(payload, maintype='application', subtype='octet-stream', filename=filename)
    return message_from_string(message.as_string())


@pytest.mark.parametrize('date', ['10.11.2026', '12.11.2026'])
def test_plant_profile_matches_changing_date(date: str) -> None:
    """Профиль Плант находит прайс независимо от даты в теме и имени вложения."""
    path = Path('tests/parse_config_example/mail.json')
    config = MailConfig.from_dict(json.loads(path.read_text()), str(path))
    profile = config.profiles['plant']
    subject = f'Прайс на аккумуляторы "План- Т" ТД СибЭлектроисточник {date}'
    filename = f'ПРАЙС 200 PLAN-T.PRO СЭИ {date}.xls'
    message = _multipart(profile.sender, subject, filename, b'price')

    assert sender_matches(message, profile.sender, sender_is_domain=profile.sender_is_domain)
    assert profile.subject_keyword is not None
    assert subject_matches(message, profile.subject_keyword)
    assert [name for name, _part in matching_attachments(message, profile.attachment_glob)] == [filename]


def test_decode_header_value_none() -> None:
    """Пустой заголовок — пустая строка."""
    assert decode_header_value(None) == ''


def test_decode_header_value_encoded() -> None:
    """RFC 2047 заголовок раскодируется."""
    assert decode_header_value(_ENCODED_PRICE) == 'прайс'


def test_decode_header_value_unknown_charset_returns_raw() -> None:
    """Неизвестная кодировка не роняет разбор: возвращается исходная строка."""
    raw = '=?unknown-charset?B?dGVzdA==?='
    assert decode_header_value(raw) == raw


def test_matching_attachments_single() -> None:
    """Находится единственное вложение по шаблону (регистр не важен)."""
    message = _multipart('a@b.ru', 'прайс', 'PRICE.XLSX', b'data')
    attachments = matching_attachments(message, '*.xlsx')
    assert [name for name, _part in attachments] == ['PRICE.XLSX']


def test_matching_attachments_no_match() -> None:
    """Несовпадающий шаблон не даёт вложений."""
    message = _multipart('a@b.ru', 'прайс', 'other.xls', b'data')
    assert matching_attachments(message, '*.xlsx') == []


def test_sender_matches_address() -> None:
    """Адрес отправителя сравнивается без учёта регистра и display-name."""
    message = _message('From: Иван <RMV@pionersib.ru>\n')
    assert sender_matches(message, 'rmv@pionersib.ru', sender_is_domain=False) is True
    assert sender_matches(message, 'other@x.ru', sender_is_domain=False) is False


def test_sender_matches_domain() -> None:
    """Домен отправителя сравнивается по окончанию адреса."""
    message = _message('From: manager@nortec-tyres.ru\n')
    assert sender_matches(message, 'nortec-tyres.ru', sender_is_domain=True) is True
    assert sender_matches(message, 'other.ru', sender_is_domain=True) is False


def test_subject_matches() -> None:
    """Тема сравнивается подстрокой без учёта регистра."""
    message = _message(f'Subject: {_ENCODED_PRICE} январь\n')
    assert subject_matches(message, 'ПРАЙС') is True
    assert subject_matches(message, 'накладная') is False


def test_attachment_content_bytes() -> None:
    """Декодированное вложение отдаёт свои байты."""
    message = _multipart('a@b.ru', 'прайс', 'price.xlsx', b'payload')
    _name, part = matching_attachments(message, '*.xlsx')[0]
    assert attachment_content(part) == b'payload'


def test_attachment_content_missing_payload() -> None:
    """Без полезной нагрузки вложение отдаёт пустые байты."""
    assert attachment_content(Message()) == b''


@pytest.mark.parametrize('body', [b'body', bytearray(b'body')])
def test_message_body_extracts_bytes(body: bytes | bytearray) -> None:
    """Тело письма берётся из второго элемента пары FETCH."""
    assert message_body((b'header', body)) == b'body'


def test_message_body_rejects_non_tuple() -> None:
    """Не парный элемент ответа не содержит тела письма."""
    assert message_body(b'garbage') is None


@pytest.mark.parametrize('entry', [(), (b'header',)])
def test_message_body_rejects_short_tuple(entry: tuple[bytes, ...]) -> None:
    """Слишком короткая пара не содержит тела письма."""
    assert message_body(entry) is None


def test_message_body_rejects_non_bytes() -> None:
    """Тело письма должно быть байтами."""
    assert message_body((b'header', 'body')) is None


_NO_HEADERS = 'X-Mailer: test\n\nbody'


@pytest.mark.parametrize(
    ('sender', 'sender_is_domain'),
    [('a@b.ru', False), ('b.ru', True)],
    ids=['address', 'domain'],
)
def test_sender_matches_without_from(sender: str, sender_is_domain: bool) -> None:
    """Письмо без From не подходит ни по адресу, ни по домену."""
    assert sender_matches(_message(_NO_HEADERS), sender, sender_is_domain=sender_is_domain) is False


@pytest.mark.parametrize(
    ('raw', 'keyword', 'expected'),
    [
        ('Subject: ПРАЙС шины\n\nbody', 'прайс', True),
        ('Subject: Счёт\n\nbody', 'прайс', False),
        (f'Subject: {_ENCODED_PRICE}\n\nbody', 'ПРАЙС', True),
        (_NO_HEADERS, 'x', False),
        (_NO_HEADERS, '', True),
    ],
    ids=['case', 'absent-word', 'encoded', 'no-subject', 'empty-keyword'],
)
def test_subject_matches_table(raw: str, keyword: str, expected: bool) -> None:
    """Слово ищется в теме без учёта регистра; письма без темы содержат только пустое слово."""
    assert subject_matches(_message(raw), keyword) is expected


def test_message_text_plain_and_html_skip_attachments() -> None:
    """В тексте письма есть plain и html части, вложения не попадают."""
    message = EmailMessage()
    message['From'] = 'a@b.ru'
    message.set_content('ссылка https://x.ru/a.xlsx')
    message.add_alternative('<a href="https://x.ru/b.xlsx">b</a>', subtype='html')
    message.add_attachment(b'data', maintype='application', subtype='octet-stream', filename='c.xlsx')
    text = message_text(message_from_string(message.as_string()))
    assert 'https://x.ru/a.xlsx' in text
    assert 'https://x.ru/b.xlsx' in text
    assert 'c.xlsx' not in text


def test_message_text_unknown_charset_falls_back() -> None:
    """Неизвестная кодировка части декодируется как utf-8."""
    raw = 'Content-Type: text/plain; charset="x-unknown"\n\nпривет'.encode()
    assert message_text(message_from_bytes(raw)) == 'привет'
