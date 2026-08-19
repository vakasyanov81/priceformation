"""fixtures for load tests"""

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(_ROOT.parent))
sys.path.insert(0, str((_ROOT / "../src").resolve()))

from cfg import init_cfg  # noqa: E402


def pytest_configure(config: pytest.Config) -> None:
    """Те же пути, что у CLI. Без порога покрытия основного набора."""
    init_cfg()
    if not _load_tests_only(config):
        return
    cov = config.pluginmanager.getplugin("_cov")
    options = getattr(cov, "options", None)
    if options is not None:
        options.cov_fail_under = 0


def _load_tests_only(config: pytest.Config) -> bool:
    args = [str(arg) for arg in config.args]
    return bool(args) and all("load_tests" in arg for arg in args)
