"""Дата письма: разбор заголовка Date и форматирование для отчёта.

Чистые функции над ``email.message.Message``: без сети и файлового IO.
"""

from datetime import datetime
from email.message import Message
from email.utils import parsedate_to_datetime

_DATE_FORMAT = '%d.%m.%Y %H:%M'


def message_datetime(message: Message) -> datetime | None:
    """Момент отправки из заголовка Date; неразобранная дата — None."""
    try:
        return parsedate_to_datetime(message.get('Date', ''))
    except (TypeError, ValueError):
        return None


def format_date(message: Message) -> str:
    """Дата письма (заголовок Date) в локальном времени, ``ДД.ММ.ГГГГ ЧЧ:ММ``."""
    moment = message_datetime(message)
    if moment is None:
        return message.get('Date', '') or 'дата неизвестна'
    return moment.astimezone().strftime(_DATE_FORMAT)
