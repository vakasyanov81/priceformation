"""Поиск самого свежего письма с прайсом по профилю поставщика."""

from dataclasses import dataclass
from datetime import datetime
from email.message import Message

from domain.mail import ImapClient
from infrastructure.mail.imap import fetch_message, search_uids, select_folder
from parsers.mail.dates import format_date, message_datetime
from parsers.mail.links import single_xlsx_link, url_filename
from parsers.mail.message import (
    attachment_content,
    decode_header_value,
    matching_attachments,
    sender_matches,
    subject_matches,
)
from parsers.mail.models import MailProfile


@dataclass(frozen=True, slots=True)
class FoundPrice:
    """Найденное письмо с пригодным вложением."""

    subject: str
    date: str
    filename: str
    payload: bytes = b''
    link: str | None = None
    when: datetime | None = None


def find_latest_price(client: ImapClient, folders: list[str], *, profile: MailProfile) -> FoundPrice | None:
    """Самое свежее письмо по профилю среди папок (отправитель, тема, вложение)."""
    best: FoundPrice | None = None
    for folder in folders:
        if not select_folder(client, folder):
            continue
        candidate = _latest_in_selected(client, profile)
        best = _newer_of(best, candidate)
    return best


def _newer_of(best: FoundPrice | None, candidate: FoundPrice | None) -> FoundPrice | None:
    """Более свежее из двух писем; None — письма нет."""
    if candidate is None:
        return best
    if best is None:
        return candidate
    if _epoch(candidate.when) > _epoch(best.when):
        return candidate
    return best


def _latest_in_selected(client: ImapClient, profile: MailProfile) -> FoundPrice | None:
    """Самое свежее подходящее письмо в уже открытой папке."""
    for uid in reversed(search_uids(client, profile.sender)):
        message = fetch_message(client, uid)
        if message is None:
            continue
        found = _price_from_message(message, profile)
        if found is not None:
            return found
    return None


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
    if profile.link_in_body:
        return _price_from_link(message)
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


def _price_from_link(message: Message) -> FoundPrice | None:
    """FoundPrice со ссылкой на xlsx из тела письма; ровно одна ссылка — иначе None."""
    link = single_xlsx_link(message)
    if link is None:
        return None
    return FoundPrice(
        subject=decode_header_value(message.get('Subject')),
        date=format_date(message),
        filename=url_filename(link),
        link=link,
        when=message_datetime(message),
    )
