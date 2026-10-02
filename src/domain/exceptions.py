"""Исключения домена: чистые классы без инфраструктуры и файлового IO."""

import traceback

from domain.exception_log import log_exception

__STACK_TRACE_LIMIT__ = 10


class CoreExceptionError(Exception):
    """Wrapper on Exception. This logic for logging exception"""

    __MESSAGE__: str | None = None

    def __init__(self, msg: str | None = None, *, detail: str | None = None) -> None:
        msg = msg or self.__MESSAGE__
        self.to_log(detail or msg)
        super().__init__(msg)

    @classmethod
    def to_log(cls, msg: str | None) -> None:
        """Собрать сообщение со стеком и отдать приёмнику логов."""
        stack = str(traceback.extract_stack(limit=__STACK_TRACE_LIMIT__))
        log_exception(f'{msg} \n {stack}')


def make_raise(message: str) -> None:
    """prepare message for raise, logging raise message"""
    raise CoreExceptionError(message)


__ALL__ = [make_raise]


class SupplierNotHavePricesError(CoreExceptionError):
    """Raise in case supplier have not price"""


class ConfigValidationError(CoreExceptionError):
    """Конфиг не соответствует ожидаемой форме: в сообщении имя файла и путь до ключа"""
