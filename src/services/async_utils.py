"""Async help logic"""

import logging
import sys
from collections.abc import Callable
from typing import Any

from domain.exceptions import CoreExceptionError, SupplierNotHavePricesError

logger = logging.getLogger(__name__)


def try_call(method: Callable[..., Any], **kwargs: Any) -> bool:
    """Try method call; False — ошибка домена залогирована, действие не выполнено."""
    try:
        method(**kwargs)
    except SupplierNotHavePricesError as exc:
        logger.warning(f'{exc}')
        sys.exit(1)
    except CoreExceptionError as exc:
        logger.error(f'{exc}')
        return False
    except KeyboardInterrupt:
        sys.exit(0)
    return True
