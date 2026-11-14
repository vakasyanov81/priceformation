"""fixtures for integration tests"""

from collections.abc import Iterator
from pathlib import Path

import pytest
import shared_fixtures

from cfg import init_cfg
from infrastructure.config.fake_config_provider import FakeConfigProvider
from parsers.base_parser.nomenclature_correction import clear_nomenclature_cache
from parsers.data_provider.manufacturer_aliases import (
    clear_manufacturer_aliases_cache,
)
from parsers.registry import clear_registry


@pytest.fixture(autouse=True)
def _log_files_untouched(monkeypatch: pytest.MonkeyPatch) -> None:
    """Разбор в тестах не обнуляет боевые файлы логов."""
    monkeypatch.setattr('services.parse_orchestrator.clear_log_files', lambda: None)


@pytest.fixture(autouse=True)
def _clear_process_file_caches() -> None:
    """Сброс модульных кэшей файлов, чтобы тесты не зависели от порядка."""
    clear_nomenclature_cache()
    clear_manufacturer_aliases_cache()


_FIXTURES = Path(__file__).resolve().parent


@pytest.fixture
def _fixture_config_provider() -> Iterator[None]:
    """Провайдер путей: конфиги и цены — из фикстур (без боевого parse_config/file_prices)."""
    init_cfg(
        FakeConfigProvider(
            _FIXTURES,
            config_folder=_FIXTURES / 'parse_config_example',
            prices_folder=_FIXTURES / 'file_prices_for_test',
            result_folder=_FIXTURES / 'result_for_test',
        ),
    )
    clear_registry()
    yield
    clear_registry()
    init_cfg()


watch_logger = shared_fixtures.watch_logger
pytest_configure = shared_fixtures.pytest_configure
_config_provider_restored = shared_fixtures.config_provider_restored
_service_provider_isolated = shared_fixtures.service_provider_isolated
