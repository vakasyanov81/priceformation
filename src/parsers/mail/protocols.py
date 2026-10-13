"""Структурный тип IMAP-клиента, нужный для поиска письма."""

from typing import Any, Protocol

type ImapResult = tuple[str, list[Any]]


class ImapClient(Protocol):
    """Минимум IMAP-клиента, нужный для поиска письма."""

    def uid(self, command: str, *args: Any) -> ImapResult: ...

    def login(self, _user: str, password: str) -> ImapResult: ...

    def select(self, _mailbox: str, _readonly: bool = False) -> ImapResult: ...

    def list(self, _directory: str, _pattern: str) -> ImapResult: ...

    def logout(self) -> ImapResult: ...
