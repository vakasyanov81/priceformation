"""Состояние JSON-режима: консольные логи молчат, пока stdout занят JSON-ответом.

Состояние живёт в ``ContextVar``, чтобы фоновые потоки разбора не переключали
режим по ошибке.
"""

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar

_json_mode: ContextVar[bool] = ContextVar('priceformation_json_mode', default=False)


def set_json_mode(active: bool) -> None:
    """Включить или выключить JSON-режим."""
    _json_mode.set(active)


def json_mode_active() -> bool:
    """Включён ли JSON-режим."""
    return _json_mode.get()


@contextmanager
def quiet_console() -> Iterator[None]:
    """Глушить консольные логи на время блока, потом вернуть обычный режим."""
    set_json_mode(True)
    try:
        yield
    finally:
        set_json_mode(False)


__ALL__ = ['json_mode_active', 'quiet_console', 'set_json_mode']
