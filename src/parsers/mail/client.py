"""Поиск свежего письма с прайсом и сохранение вложения.

Сетевой адаптер поверх IMAP: подключение (см. ``doh``), отбор письма по
профилю поставщика и запись вложения в ``file_prices``.
"""

from __future__ import annotations

import imaplib
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from email import message_from_bytes
from email.message import Message
from pathlib import Path
from typing import Any

from infrastructure.config.mail_credentials import MailCredentials
from parsers.mail.dates import format_date, message_datetime
from parsers.mail.doh import open_client
from parsers.mail.errors import MailConnectionError
from parsers.mail.message import (
    attachment_content,
    decode_header_value,
    matching_attachments,
    message_body,
    sender_matches,
    subject_matches,
)
from parsers.mail.models import MailAccount, MailProfile
from parsers.mail.protocols import ImapClient

logger = logging.getLogger(__name__)

type _ListEntry = tuple[frozenset[bytes], str | None, str]

_ALLOWED_EXTENSIONS = ('.xls', '.xlsx')
_PRICE_STEM = 'price'
_STATUS_OK = 'OK'
_MSG_FOLDER_FAILED = 'Не удалось открыть папку {folder!r}'
_LIST_LINE = re.compile(rb'^\((?P<flags>[^)]*)\)\s+(?P<delimiter>(?i:NIL)|"(?:\\.|[^"])*")\s+(?P<name>.+)$')
_MAILBOX_SPECIALS = frozenset('(){ %*"\\')
_NOSELECT = b'\x5cNoselect'


@dataclass(frozen=True, slots=True)
class FoundPrice:
    """Найденное письмо с пригодным вложением."""

    subject: str
    date: str
    filename: str
    payload: bytes
    when: datetime | None = None


def connect(account: MailAccount, credentials: MailCredentials) -> ImapClient:
    """Подключиться, войти и открыть папку только для чтения."""
    client = open_client(account)
    try:
        client.login(credentials.login, credentials.password)
    except imaplib.IMAP4.error:
        client.logout()
        raise
    status, _ = client.select(_mailbox_arg(account.folder), True)
    if status != _STATUS_OK:
        client.logout()
        raise MailConnectionError(_MSG_FOLDER_FAILED.format(folder=account.folder))
    return client


def list_price_folders(client: ImapClient, root: str) -> list[str]:
    """Папка root и все её подпапки (кроме служебных) — где искать письма."""
    status, raw = client.list('""', '*')
    if status != _STATUS_OK:
        return [root]
    return _subtree_folders(raw, root)


def find_latest_price(client: ImapClient, folders: list[str], *, profile: MailProfile) -> FoundPrice | None:
    """Самое свежее письмо по профилю среди папок (отправитель, тема, вложение)."""
    best: FoundPrice | None = None
    for folder in folders:
        if not _select(client, folder):
            continue
        candidate = _latest_in_selected(client, profile)
        best = _newer_of(best, candidate)
    return best


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


def _subtree_folders(raw: list[Any], root: str) -> list[str]:
    """Корень root первым, затем его подпапки из строк ответа LIST."""
    entries = _parsed_entries(raw)
    delimiter = _first_delimiter(entries)
    return [root, *_names_in_subtree(entries, root, delimiter)]


def _parsed_entries(raw: list[Any]) -> list[_ListEntry]:
    """Разобранные строки LIST без мусора."""
    parsed = [_parse_list_entry(entry) for entry in raw]
    return [entry for entry in parsed if entry is not None]


def _first_delimiter(entries: list[_ListEntry]) -> str | None:
    """Первый непустой разделитель иерархии среди папок."""
    for _flags, delimiter, _name in entries:
        if delimiter is not None:
            return delimiter
    return None


def _names_in_subtree(entries: list[_ListEntry], root: str, delimiter: str | None) -> list[str]:
    """Имена вложенных папок root (без служебных и без самого root)."""
    names: list[str] = []
    for flags, _delim, name in entries:
        if _keep_mailbox(flags, name, root, delimiter):
            names.append(name)
    return names


def _keep_mailbox(flags: frozenset[bytes], name: str, root: str, delimiter: str | None) -> bool:
    """Папка не служебная и вложена в root."""
    if _NOSELECT in flags:
        return False
    return _is_descendant(name, root, delimiter)


def _newer_of(best: FoundPrice | None, candidate: FoundPrice | None) -> FoundPrice | None:
    """Более свежее из двух писем; None — письма нет."""
    if candidate is None:
        return best
    if best is None:
        return candidate
    if _epoch(candidate.when) > _epoch(best.when):
        return candidate
    return best


def _select(client: ImapClient, folder: str) -> bool:
    """Открыть папку только для чтения; недоступная — предупреждение и False."""
    status, _ = client.select(_mailbox_arg(folder), True)
    if status != _STATUS_OK:
        logger.warning(f'Письма не искать: не удалось открыть папку {folder!r}.')
        return False
    return True


def _latest_in_selected(client: ImapClient, profile: MailProfile) -> FoundPrice | None:
    """Самое свежее подходящее письмо в уже открытой папке."""
    for uid in reversed(_search_uids(client, profile.sender)):
        message = _fetch_message(client, uid)
        if message is None:
            continue
        found = _price_from_message(message, profile)
        if found is not None:
            return found
    return None


def _is_descendant(name: str, root: str, delimiter: str | None) -> bool:
    """Вложена ли папка в root по разделителю иерархии (сам root — нет)."""
    if delimiter is None:
        return False
    return name.startswith(root + delimiter)


def _parse_list_entry(entry: object) -> _ListEntry | None:
    """Флаги, разделитель и имя из строки ответа LIST; мусор — None."""
    if not isinstance(entry, (bytes, bytearray)):
        return None
    match = _LIST_LINE.match(bytes(entry).strip())
    if match is None:
        return None
    flags = frozenset(match.group('flags').split())
    delimiter = _delimiter(match.group('delimiter'))
    name = _unquote(match.group('name'))
    return flags, delimiter, name


def _delimiter(token: bytes) -> str | None:
    """Разделитель иерархии из поля LIST; NIL — None."""
    if token.upper() == b'NIL':
        return None
    return _unquote(token) or None


def _mailbox_arg(name: str) -> str:
    """Имя папки для SELECT: спецсимволы требуют кавычек (imaplib не квотит сам)."""
    if name and not any(char in _MAILBOX_SPECIALS for char in name):
        return name
    escaped = name.replace('\\', r'\\').replace('"', r'\"')
    return f'"{escaped}"'


def _unquote(token: bytes) -> str:
    """Снять кавычки и обратные слэши со строкового токена IMAP."""
    text = token.decode('utf-8', 'replace').strip()
    if not _is_quoted(text):
        return text
    return re.sub(r'\\(.)', r'\1', text[1:-1])


def _is_quoted(text: str) -> bool:
    """Строка — IMAP-строка в двойных кавычках."""
    if len(text) <= 1:
        return False
    return text.startswith('"') and text.endswith('"')


def _epoch(when: datetime | None) -> float:
    """Сортируемое время письма; неизвестная дата — как самое старое."""
    if when is None:
        return float('-inf')
    return when.timestamp()


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
        subject=decode_header_value(message.get('Subject')),
        date=format_date(message),
        filename=filename,
        payload=attachment_content(part),
        when=message_datetime(message),
    )


def _search_uids(client: ImapClient, sender: str) -> list[bytes]:
    """UID всех писем от отправителя (по возрастанию)."""
    status, raw = client.uid('SEARCH', None, 'FROM', sender)
    if status != _STATUS_OK or not raw:
        return []
    first = raw[0]
    if not isinstance(first, (bytes, bytearray)):
        return []
    return list(bytes(first).split())


def _fetch_message(client: ImapClient, uid: bytes) -> Message | None:
    """Разобранное письмо по UID; нет тела — None."""
    status, raw = client.uid('FETCH', uid, '(RFC822)')
    if status != _STATUS_OK or not raw:
        return None
    for entry in raw:
        body = message_body(entry)
        if body is not None:
            return message_from_bytes(body)
    return None
