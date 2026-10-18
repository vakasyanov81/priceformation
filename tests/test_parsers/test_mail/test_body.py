"""Текст тела письма: какие части берутся и как декодируются."""

import email
from email.message import EmailMessage, Message

from parsers.mail.body import message_text


def _raw(content_type: str, body: bytes, extra_headers: str = '') -> Message:
    head = f'Content-Type: {content_type}\n{extra_headers}\n'.encode()
    return email.message_from_bytes(head + body)


def test_plain_and_html_parts_are_joined_with_newline() -> None:
    """Текстовые части склеиваются переводом строки, а не склеиваются встык."""
    message = EmailMessage()
    message.set_content('первая')
    message.add_alternative('<p>вторая</p>', subtype='html')

    assert message_text(message) == 'первая\n\n<p>вторая</p>\n'


def test_text_attachment_is_not_body() -> None:
    """Текстовое вложение с именем файла в тело не попадает."""
    message = EmailMessage()
    message.set_content('тело')
    message.add_attachment('вложение', filename='note.txt')

    assert message_text(message) == 'тело\n'


def test_declared_charset_is_used() -> None:
    """Объявленная кодировка тела применяется, а не подменяется utf-8."""
    message = _raw('text/plain; charset=windows-1251', 'Привет'.encode('cp1251'))

    assert message_text(message) == 'Привет'


def test_undeclared_charset_falls_back_to_utf8() -> None:
    """Без объявленной кодировки тело читается как utf-8."""
    message = _raw('text/plain', 'Привет'.encode())

    assert message_text(message) == 'Привет'


def test_undeclared_charset_replaces_invalid_bytes() -> None:
    """Не-utf-8 байты без объявленной кодировки не роняют разбор: заменяются на �."""
    message = _raw('text/plain', 'Привет'.encode('cp1251'))

    assert message_text(message) == '�' * 6


def test_invalid_bytes_in_declared_charset_are_replaced() -> None:
    """Байт, которого нет в объявленной кодировке, заменяется, остальной текст сохраняется."""
    message = _raw('text/plain; charset=windows-1251', 'Привет'.encode('cp1251') + b'\x98')

    assert message_text(message) == 'Привет�'


def test_unknown_charset_falls_back_to_utf8_with_replace() -> None:
    """Неизвестная кодировка: читаем как utf-8, невалидные байты заменяются."""
    message = _raw('text/plain; charset=x-no-such-charset', 'ок'.encode() + b'\xff')

    assert message_text(message) == 'ок�'
