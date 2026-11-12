"""Async help logic"""

import logging
import sys
from collections.abc import Callable
from typing import Any

from domain.exceptions import CoreExceptionError, SupplierNotHavePricesError

logger = logging.getLogger(__name__)


def try_call(method: Callable[..., Any], **kwargs: Any) -> bool:
    """Try method call; False — ошибка домена залогирована, действие не выполнено."""
    return try_call_with_result(method, **kwargs)[0]


def try_call_with_result[ReturnValue](
    method: Callable[..., ReturnValue], **kwargs: Any
) -> tuple[bool, ReturnValue | None]:
    """Вернуть отсутствие ошибки и результат вызова; при доменной ошибке результат — None."""
    outcome: ReturnValue | None = None
    try:
        outcome = method(**kwargs)
    except SupplierNotHavePricesError as exc:
        logger.warning(f'{exc}')
        sys.exit(1)
    except CoreExceptionError as exc:
        logger.error(f'{exc}')
        return False, None
    except KeyboardInterrupt:
        sys.exit(0)
    return True, outcome
