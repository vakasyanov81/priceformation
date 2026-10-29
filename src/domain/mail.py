"""Порты и ошибки получения прайсов из почты."""

from typing import Any, Protocol

from domain.exceptions import CoreExceptionError

type ImapResult = tuple[str, list[Any]]


class ImapClient(Protocol):
    """Минимум IMAP-клиента, нужный для поиска письма."""

    def uid(self, command: str, *args: Any) -> ImapResult: ...

    def login(self, _user: str, password: str) -> ImapResult: ...

    def select(self, _mailbox: str, _readonly: bool = False) -> ImapResult: ...

    def list(self, _directory: str, _pattern: str) -> ImapResult: ...

    def logout(self) -> ImapResult: ...


class MailConfigNotFoundError(CoreExceptionError):
    """Файл настроек почты parse_config/mail.json не найден."""


class MailConnectionError(CoreExceptionError):
    """Не удалось подключиться к IMAP-серверу или открыть папку."""


class PriceDownloadError(CoreExceptionError):
    """Не удалось скачать прайс по ссылке из письма."""
