"""Async help logic"""

import logging
import sys
from collections.abc import Callable
from typing import Any

from domain.exceptions import CoreExceptionError, SupplierNotHavePricesError

logger = logging.getLogger(__name__)


def try_call(method: Callable[..., Any], **kwargs: Any) -> None:
    """Try method call"""
    try:
        method(**kwargs)
    except SupplierNotHavePricesError as exc:
        logger.warning(f'{exc}')
        sys.exit(1)
    except CoreExceptionError as exc:
        logger.error(f'{exc}')
    except KeyboardInterrupt:
        sys.exit(0)
