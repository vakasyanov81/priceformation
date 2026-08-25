"""
global fixtures
"""

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(_ROOT.parent))
sys.path.insert(0, str((_ROOT / "../src").resolve()))
sys.path.insert(0, str((_ROOT / "../tests").resolve()))

from cfg import init_cfg  # noqa: E402
from parsers.base_parser.nomenclature_correction import clear_nomenclature_cache  # noqa: E402
from parsers.data_provider.manufacturer_aliases import (  # noqa: E402
    clear_manufacturer_aliases_cache,
)


def pytest_configure() -> None:
    """Композиция тестов: те же пути, что и init_cfg в run.main."""
    init_cfg()


@pytest.fixture(autouse=True)
def _clear_process_file_caches() -> None:
    """Сброс модульных кэшей файлов, чтобы тесты не зависели от порядка."""
    clear_nomenclature_cache()
    clear_manufacturer_aliases_cache()
