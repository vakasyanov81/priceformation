"""global fixtures"""

import sys
from collections.abc import Iterator
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(_ROOT.parent))
sys.path.insert(0, str((_ROOT / '../src').resolve()))
sys.path.insert(0, str((_ROOT / '../tests').resolve()))

from cfg import init_cfg  # noqa: E402
from parsers.base_parser.nomenclature_correction import clear_nomenclature_cache  # noqa: E402
from parsers.data_provider.manufacturer_aliases import (  # noqa: E402
    clear_manufacturer_aliases_cache,
)
from services.configure import configure_services  # noqa: E402
from services.service_provider import ServiceProvider  # noqa: E402


def pytest_configure() -> None:
    """Композиция тестов: те же пути, что и init_cfg в run.main."""
    init_cfg()
    configure_services()


@pytest.fixture(autouse=True)
def _clear_process_file_caches() -> None:
    """Сброс модульных кэшей файлов, чтобы тесты не зависели от порядка."""
    clear_nomenclature_cache()
    clear_manufacturer_aliases_cache()


@pytest.fixture(autouse=True)
def _service_provider_isolated() -> Iterator[None]:
    """DI-контейнер: базовая сборка до теста, сброс после (без глобальных завязок)."""
    ServiceProvider.clear()
    configure_services()
    yield
    ServiceProvider.reset()
