"""Куда домен пишет сообщения об исключениях: приёмник назначает инфраструктура."""

from collections.abc import Callable

type ExceptionLogSink = Callable[[str], None]


class _CurrentExceptionLog:
    """Приёмник на процесс; без него сообщения просто не пишутся."""

    sink: ExceptionLogSink | None = None


def set_exception_log_sink(sink: ExceptionLogSink | None) -> None:
    """Назначить приёмник; None — не писать ничего (логи не настроены)."""
    _CurrentExceptionLog.sink = sink


def log_exception(message: str) -> None:
    """Передать сообщение приёмнику, если он настроен."""
    sink = _CurrentExceptionLog.sink
    if sink is not None:
        sink(message)
