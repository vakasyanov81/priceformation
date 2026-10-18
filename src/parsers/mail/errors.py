"""Ошибки загрузки прайсов поставщиков из почты."""

from domain.exceptions import CoreExceptionError


class MailConfigNotFoundError(CoreExceptionError):
    """Файл настроек почты parse_config/mail.json не найден."""


class MailConnectionError(CoreExceptionError):
    """Не удалось подключиться к IMAP-серверу или открыть папку."""


class PriceDownloadError(CoreExceptionError):
    """Не удалось скачать прайс по ссылке из письма."""
