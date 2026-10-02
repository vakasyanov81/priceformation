"""fixtures for infrastructure tests"""

import logging
from collections.abc import Iterator

import pytest

from infrastructure.logging.json_mode import set_json_mode


@pytest.fixture(autouse=True)
def _root_logging_restored() -> Iterator[None]:
    """Настройка корневого логгера не должна протекать между тестами."""
    root = logging.getLogger()
    saved_handlers = list(root.handlers)
    saved_level = root.level
    yield
    set_json_mode(False)
    for log_handler in list(root.handlers):
        if log_handler not in saved_handlers:
            root.removeHandler(log_handler)
            log_handler.close()
    for saved_log_handler in saved_handlers:
        if saved_log_handler not in root.handlers:
            root.addHandler(saved_log_handler)
    root.setLevel(saved_level)
