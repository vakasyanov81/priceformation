"""Типизированная модель parse_config/mail.json.

Ключ профиля — папка поставщика в ``file_prices``; прайс кладётся в
``file_prices/<папка>/price.xlsx``. Адрес ящика и доступы в модели не входят:
логин и пароль берутся отдельно (см. infrastructure/config/mail_credentials.py).
"""

from dataclasses import dataclass
from typing import Any

from parsers.data_provider.json_fields import (
    RawConfig,
    as_config_object,
    read_object,
    read_zero_one_flag,
)
from parsers.vendor_config.fields import read_int, read_text

DEFAULT_IMAP_HOST = 'imap.timeweb.ru'
DEFAULT_IMAP_PORT = 993
DEFAULT_IMAP_FOLDER = 'INBOX'


@dataclass(frozen=True, slots=True)
class MailProfile:
    """Правила поиска письма с прайсом одного поставщика."""

    sender: str
    sender_is_domain: bool
    subject_keyword: str | None
    attachment_glob: str
    enabled: bool
    link_in_body: bool = False

    @classmethod
    def from_dict(cls, raw: Any, where: str) -> MailProfile:
        """Разобрать профиль поставщика из объекта JSON."""
        payload = as_config_object(raw, where)
        link_in_body = read_zero_one_flag(payload, 'link_in_body', where, default=False)
        return cls(
            sender=read_text(payload, 'sender', where),
            sender_is_domain=read_zero_one_flag(payload, 'sender_is_domain', where, default=False),
            subject_keyword=_read_optional_text(payload, 'subject_keyword', where),
            attachment_glob=read_text(payload, 'attachment_glob', where, '' if link_in_body else None),
            enabled=read_zero_one_flag(payload, 'enabled', where, default=True),
            link_in_body=link_in_body,
        )


@dataclass(frozen=True, slots=True)
class MailAccount:
    """Параметры IMAP-подключения."""

    host: str
    port: int
    folder: str

    @classmethod
    def from_dict(cls, payload: RawConfig, where: str) -> MailAccount:
        """Разобрать секцию ``imap``, уже проверенную как объект (``read_object``)."""
        return cls(
            host=read_text(payload, 'host', where, DEFAULT_IMAP_HOST),
            port=read_int(payload, 'port', where, DEFAULT_IMAP_PORT),
            folder=read_text(payload, 'folder', where, DEFAULT_IMAP_FOLDER),
        )


@dataclass(frozen=True, slots=True)
class MailConfig:
    """Настройки почты целиком: IMAP-подключение и профили поставщиков."""

    account: MailAccount
    profiles: dict[str, MailProfile]

    @classmethod
    def from_dict(cls, raw: Any, where: str) -> MailConfig:
        """Разобрать parse_config/mail.json."""
        payload = as_config_object(raw, where)
        return cls(
            account=MailAccount.from_dict(read_object(payload, 'imap', where), f'{where} → imap'),
            profiles=_read_profiles(read_object(payload, 'profiles', where), where),
        )

    def enabled_profiles(self) -> dict[str, MailProfile]:
        """Профили с включённым флагом enabled, в порядке файла."""
        return {folder: profile for folder, profile in self.profiles.items() if profile.enabled}


def _read_profiles(profiles_raw: RawConfig, where: str) -> dict[str, MailProfile]:
    """Разобрать секцию ``profiles``: папка поставщика → профиль."""
    profiles: dict[str, MailProfile] = {}
    for folder, profile_raw in profiles_raw.items():
        profiles[folder] = MailProfile.from_dict(profile_raw, f'{where} → profiles.{folder}')
    return profiles


def _read_optional_text(payload: RawConfig, key: str, where: str) -> str | None:
    """Прочитать необязательную непустую строку; ключа нет — None."""
    if key not in payload:
        return None
    return read_text(payload, key, where)
