"""Текст тела письма для поиска ссылок.

Чистые функции над ``email.message.Message``: без сети и файлового IO.
"""

from email.message import Message
from typing import Any

_MULTIPART = 'multipart'
_TEXT_TYPES = ('text/plain', 'text/html')


def message_text(message: Message) -> str:
    """Текст тела письма (plain и html) без вложений."""
    chunks = [_part_text(part) for part in message.walk() if _is_body_part(part)]
    return '\n'.join(chunk for chunk in chunks if chunk is not None)


def _is_body_part(part: Message) -> bool:
    """Часть — текстовое тело, а не вложение и не контейнер."""
    if part.get_content_maintype() == _MULTIPART or part.get_filename():
        return False
    return part.get_content_type() in _TEXT_TYPES


def _part_text(part: Message) -> str | None:
    """Декодированный текст части; нераспознанная нагрузка — None."""
    payload: Any = part.get_payload(decode=True)
    if not isinstance(payload, bytes):
        return None
    try:
        return payload.decode(part.get_content_charset() or 'utf-8', 'replace')
    except LookupError:
        return payload.decode('utf-8', 'replace')
