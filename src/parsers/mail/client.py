"""Поиск свежего письма с прайсом и сохранение вложения.

Сетевой адаптер поверх IMAP: подключение (см. ``doh``), отбор письма по
профилю поставщика и запись вложения в ``file_prices``.
"""

from __future__ import annotations

import imaplib
from dataclasses import dataclass
from email import message_from_bytes
from email.message import Message
from pathlib import Path

from infrastructure.config.mail_credentials import MailCredentials
from parsers.mail.doh import open_client
from parsers.mail.errors import MailConnectionError
from parsers.mail.message import (
    attachment_content,
    decode_header_value,
    format_date,
    matching_attachments,
    message_body,
    sender_matches,
    subject_matches,
)
from parsers.mail.models import MailAccount, MailProfile
from parsers.mail.protocols import ImapClient

_ALLOWED_EXTENSIONS = ('.xls', '.xlsx')
_PRICE_STEM = 'price'
_MSG_FOLDER_FAILED = 'Не удалось открыть папку {folder!r}'


@dataclass(frozen=True, slots=True)
class FoundPrice:
    """Найденное письмо с пригодным вложением."""

    subject: str
    date: str
    filename: str
    payload: bytes


def connect(account: MailAccount, credentials: MailCredentials) -> ImapClient:
    """Подключиться, войти и открыть папку только для чтения."""
    client = open_client(account)
    try:
        client.login(credentials.login, credentials.password)
    except imaplib.IMAP4.error:
        client.logout()
        raise
    status, _ = client.select(account.folder, readonly=True)
    if status != 'OK':
        client.logout()
        raise MailConnectionError(_MSG_FOLDER_FAILED.format(folder=account.folder))
    return client


def find_latest_price(client: ImapClient, *, profile: MailProfile) -> FoundPrice | None:
    """Самое свежее письмо по профилю поставщика (отправитель, тема, вложение)."""
    for uid in reversed(_search_uids(client, profile.sender)):
        message = _fetch_message(client, uid)
        if message is None:
            continue
        found = _price_from_message(message, profile)
        if found is not None:
            return found
    return None


def save_price(dest: Path, payload: bytes) -> None:
    """Записать прайс в dest, убрав устаревший файл с другим расширением."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    for extension in _ALLOWED_EXTENSIONS:
        stale = dest.parent / f'{_PRICE_STEM}{extension}'
        if stale != dest:
            stale.unlink(missing_ok=True)
    temporary = dest.with_name(f'{dest.name}.tmp')
    temporary.write_bytes(payload)
    temporary.replace(dest)


def _price_from_message(message: Message, profile: MailProfile) -> FoundPrice | None:
    """Собрать FoundPrice, если письмо и ровно одно вложение подходят профилю."""
    sender_ok = sender_matches(message, profile.sender, sender_is_domain=profile.sender_is_domain)
    if not sender_ok:
        return None
    if profile.subject_keyword is not None and not subject_matches(message, profile.subject_keyword):
        return None
    attachments = matching_attachments(message, profile.attachment_glob)
    if len(attachments) != 1:
        return None
    filename, part = attachments[0]
    return FoundPrice(
        subject=decode_header_value(message.get('Subject', '')),
        date=format_date(message),
        filename=filename,
        payload=attachment_content(part),
    )


def _search_uids(client: ImapClient, sender: str) -> list[bytes]:
    """UID всех писем от отправителя (по возрастанию)."""
    status, raw = client.uid('SEARCH', None, 'FROM', sender)
    if status != 'OK' or not raw:
        return []
    first = raw[0]
    if not isinstance(first, (bytes, bytearray)):
        return []
    return list(bytes(first).split())


def _fetch_message(client: ImapClient, uid: bytes) -> Message | None:
    """Разобранное письмо по UID; нет тела — None."""
    status, raw = client.uid('FETCH', uid, '(RFC822)')
    if status != 'OK' or not raw:
        return None
    for entry in raw:
        body = message_body(entry)
        if body is not None:
            return message_from_bytes(body)
    return None
