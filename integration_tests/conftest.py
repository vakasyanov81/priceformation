"""fixtures for integration tests"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(_ROOT.parent))
sys.path.insert(0, str((_ROOT / "../src").resolve()))
sys.path.insert(0, str(_ROOT))

from cfg import init_cfg  # noqa: E402


def pytest_configure() -> None:
    """Композиция интеграционных тестов: пути логов и parse_config."""
    init_cfg()
