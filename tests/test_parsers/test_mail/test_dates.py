"""Разбор даты письма: заголовок Date и формат для отчёта."""

from email import message_from_string
from email.message import Message
from email.utils import parsedate_to_datetime

from parsers.mail.dates import format_date, message_datetime

_RAW = 'Wed, 01 Jan 2025 12:00:00 +0300'


def _message(raw: str) -> Message:
    return message_from_string(raw)


def test_message_datetime_valid() -> None:
    """Валидный заголовок Date разбирается в момент времени."""
    assert message_datetime(_message(f'Date: {_RAW}\n')) == parsedate_to_datetime(_RAW)


def test_message_datetime_invalid_returns_none() -> None:
    """Неразбираемая дата не даёт момента времени."""
    assert message_datetime(_message('Date: not-a-date\n')) is None


def test_format_date_valid() -> None:
    """Валидная дата приводится к локальному времени формата ДД.ММ.ГГГГ ЧЧ:ММ."""
    expected = parsedate_to_datetime(_RAW).astimezone().strftime('%d.%m.%Y %H:%M')
    assert format_date(_message(f'Date: {_RAW}\n')) == expected


def test_format_date_invalid_returns_raw() -> None:
    """Неразбираемая дата возвращается как есть."""
    assert format_date(_message('Date: not-a-date\n')) == 'not-a-date'


def test_format_date_missing() -> None:
    """Без заголовка Date — понятная подпись."""
    assert format_date(_message('Subject: x\n')) == 'дата неизвестна'


def test_message_datetime_missing() -> None:
    """Без заголовка Date момента отправки нет."""
    assert message_datetime(_message('Subject: x\n')) is None
