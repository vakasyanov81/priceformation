"""IMAP-операции и файловое сохранение найденного вложения."""

from __future__ import annotations

import imaplib
import logging
import re
from email import message_from_bytes
from email.message import Message
from pathlib import Path
from typing import Any

from domain.mail import ImapClient, MailConnectionError
from infrastructure.config.mail_credentials import MailCredentials
from infrastructure.mail.doh import open_client

logger = logging.getLogger(__name__)

type _ListEntry = tuple[frozenset[bytes], str | None, str]

_ALLOWED_EXTENSIONS = ('.xls', '.xlsx')
_PRICE_STEM = 'price'
_STATUS_OK = 'OK'
_MSG_FOLDER_FAILED = 'Не удалось открыть папку {folder!r}'
_LIST_LINE = re.compile(rb'^\((?P<flags>[^)]*)\)\s+(?P<delimiter>(?i:NIL)|"(?:\\.|[^"])*")\s+(?P<name>.+)$')
_MAILBOX_SPECIALS = frozenset('(){ %*"\\')
_NOSELECT = b'\x5cNoselect'


def connect(host: str, port: int, folder: str, credentials: MailCredentials) -> ImapClient:
    """Подключиться, войти и открыть папку только для чтения."""
    client = open_client(host, port)
    try:
        client.login(credentials.login, credentials.password)
    except imaplib.IMAP4.error:
        client.logout()
        raise
    status, _ = client.select(_mailbox_arg(folder), True)
    if status != _STATUS_OK:
        client.logout()
        raise MailConnectionError(_MSG_FOLDER_FAILED.format(folder=folder))
    return client


def list_price_folders(client: ImapClient, root: str) -> list[str]:
    """Папка root и все её подпапки (кроме служебных) — где искать письма."""
    status, raw = client.list('""', '*')
    if status != _STATUS_OK:
        return [root]
    return _subtree_folders(raw, root)


def select_folder(client: ImapClient, folder: str) -> bool:
    """Открыть папку только для чтения; недоступная — предупреждение и False."""
    status, _ = client.select(_mailbox_arg(folder), True)
    if status != _STATUS_OK:
        logger.warning(f'Письма не искать: не удалось открыть папку {folder!r}.')
        return False
    return True


def search_uids(client: ImapClient, sender: str) -> list[bytes]:
    """UID всех писем от отправителя (по возрастанию)."""
    status, raw = client.uid('SEARCH', None, 'FROM', sender)
    if status != _STATUS_OK or not raw:
        return []
    first = raw[0]
    if not isinstance(first, (bytes, bytearray)):
        return []
    return list(bytes(first).split())


def fetch_message(client: ImapClient, uid: bytes) -> Message | None:
    """Разобранное письмо по UID; нет тела — None."""
    status, raw = client.uid('FETCH', uid, '(RFC822)')
    if status != _STATUS_OK or not raw:
        return None
    for entry in raw:
        body = _message_body(entry)
        if body is not None:
            return message_from_bytes(body)
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


def _message_body(entry: Any) -> bytes | None:
    """Тело письма из элемента ответа FETCH, если он его содержит."""
    if not isinstance(entry, tuple) or len(entry) <= 1:
        return None
    body = entry[1]
    if isinstance(body, (bytes, bytearray)):
        return bytes(body)
    return None


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
