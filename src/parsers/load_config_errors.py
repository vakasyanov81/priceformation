"""Ошибки загрузки файлов настроек в parse_config."""

from core.exceptions import CoreExceptionError


class InvalidConfigKindError(CoreExceptionError):
    """Имя или расширение файла не из допустимого набора."""


class InvalidConfigJsonError(CoreExceptionError):
    """Файл с расширением json не содержит JSON."""


class ConfigFileNotFoundError(CoreExceptionError):
    """Исходный файл настроек не найден."""
