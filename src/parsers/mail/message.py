"""Разбор письма: отправитель, тема и подходящие вложения.

Чистые функции над ``email.message.Message``: без сети и файлового IO.
"""

from email.header import decode_header, make_header
from email.message import Message
from email.utils import parseaddr
from fnmatch import fnmatchcase
from typing import Any

_MULTIPART = 'multipart'


def decode_header_value(raw: str | None) -> str:
    """Раскодировать RFC 2047 заголовок (тема, имя вложения) в строку."""
    if not raw:
        return ''
    try:
        return str(make_header(decode_header(raw)))
    except (ValueError, LookupError):
        return raw


def matching_attachments(message: Message, glob_pattern: str) -> list[tuple[str, Message]]:
    """Вложения, чьё имя соответствует шаблону (регистр не важен), в порядке письма."""
    attachments: list[tuple[str, Message]] = []
    for part in message.walk():
        if part.get_content_maintype() == _MULTIPART:
            continue
        filename = decode_header_value(part.get_filename())
        if fnmatchcase(filename.lower(), glob_pattern.lower()):
            attachments.append((filename, part))
    return attachments


def sender_matches(message: Message, sender: str, *, sender_is_domain: bool) -> bool:
    """Совпадает ли From письма с адресом или доменом отправителя (без учёта регистра)."""
    _, address = parseaddr(decode_header_value(message.get('From', '')))
    address = address.lower()
    if sender_is_domain:
        return address.endswith(f'@{sender.lower()}')
    return address == sender.lower()


def subject_matches(message: Message, keyword: str) -> bool:
    """Есть ли слово (подстрока) в теме письма без учёта регистра."""
    subject = decode_header_value(message.get('Subject', ''))
    return keyword.casefold() in subject.casefold()


def attachment_content(part: Message) -> bytes:
    """Декодированное содержимое вложения; нераспознанное — пустые байты."""
    payload = part.get_payload(decode=True)
    if isinstance(payload, bytes):
        return payload
    return b''


def message_body(entry: Any) -> bytes | None:
    """Тело письма из элемента ответа FETCH, если он его содержит."""
    if not isinstance(entry, tuple) or len(entry) <= 1:
        return None
    body = entry[1]
    if isinstance(body, (bytes, bytearray)):
        return bytes(body)
    return None
