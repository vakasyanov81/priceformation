"""
global fixtures
"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(_ROOT.parent))
sys.path.insert(0, str((_ROOT / "../src").resolve()))
sys.path.insert(0, str((_ROOT / "../tests").resolve()))

from cfg import init_cfg  # noqa: E402


def pytest_configure() -> None:
    """Композиция тестов: те же пути, что и init_cfg в run.main."""
    init_cfg()
