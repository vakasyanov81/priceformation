"""Разбор письма: заголовки, дата, вложения, отправитель."""

from email import message_from_string
from email.message import EmailMessage, Message

from parsers.mail.message import (
    attachment_content,
    decode_header_value,
    matching_attachments,
    message_body,
    sender_matches,
    subject_matches,
)

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


def test_message_body_extracts_bytes() -> None:
    """Тело письма берётся из второго элемента пары FETCH."""
    assert message_body((b'header', b'body')) == b'body'


def test_message_body_rejects_non_tuple() -> None:
    """Не парный элемент ответа не содержит тела письма."""
    assert message_body(b'garbage') is None


def test_message_body_rejects_short_tuple() -> None:
    """Слишком короткая пара не содержит тела письма."""
    assert message_body((b'header',)) is None


def test_message_body_rejects_non_bytes() -> None:
    """Тело письма должно быть байтами."""
    assert message_body((b'header', 'body')) is None
