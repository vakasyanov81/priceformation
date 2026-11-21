"""Результаты получения прайсов из почты."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MailFetchResult:
    """Результат выгрузки прайса одного поставщика."""

    folder: str
    subject: str
    date: str
    filename: str
    path: str


@dataclass(frozen=True, slots=True)
class MailFetchReport:
    """Скачанные прайсы и статусы по почтовым профилям."""

    fetched: list[MailFetchResult]
    statuses: dict[str, str]

    @classmethod
    def from_profiles(cls, profiles: Iterable[str], fetched: list[MailFetchResult]) -> MailFetchReport:
        """Отметить каждый профиль по наличию скачанного прайса."""
        statuses = dict.fromkeys(profiles, 'skipped')
        statuses.update(dict.fromkeys((entry.folder for entry in fetched), 'ok'))
        return cls(fetched, statuses)
