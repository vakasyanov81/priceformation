"""tests for ConfigProvider: процессный провайдер и файловая реализация"""

import datetime
from collections.abc import Iterator
from pathlib import Path

import pytest

from core.config_provider import (
    ConfigProviderNotConfiguredError,
    _CurrentConfigProvider,
    get_config_provider,
    set_config_provider,
)
from core.log_paths import LogPaths
from infrastructure.config.fake_config_provider import FakeConfigProvider
from infrastructure.config.file_config_provider import FileConfigProvider

_ROOT = '/var/priceformation'
_CONFIG_FILE = 'vendor_list.json'
_SUPPLIER_FOLDER = 'poshk'
_LOG_FOLDER = '/var/logs'


@pytest.fixture
def _restore_provider() -> Iterator[None]:
    previous = _CurrentConfigProvider.configured  # noqa: WPS437
    yield
    _CurrentConfigProvider.configured = previous  # noqa: WPS437


def test_set_provider_is_used_by_get(_restore_provider: None, tmp_path: Path) -> None:
    """set_config_provider сохраняет провайдер для get_config_provider."""
    provider = FakeConfigProvider(tmp_path)
    set_config_provider(provider)
    assert get_config_provider() is provider


def test_get_provider_requires_configure(_restore_provider: None) -> None:
    """без set_config_provider — явная ошибка."""
    _CurrentConfigProvider.configured = None  # noqa: WPS437
    with pytest.raises(ConfigProviderNotConfiguredError, match='Config provider is not configured'):
        get_config_provider()


def test_config_provider_not_configured_error_message() -> None:
    """ConfigProviderNotConfiguredError содержит стандартное сообщение."""
    assert str(ConfigProviderNotConfiguredError()) == 'Config provider is not configured'


def test_file_provider_paths_from_root() -> None:
    """FileConfigProvider собирает пути от переданного корня."""
    provider = FileConfigProvider(_ROOT)
    assert provider.project_root == _ROOT
    assert provider.config_file(_CONFIG_FILE) == f'{_ROOT}/parse_config/{_CONFIG_FILE}'
    assert provider.price_folder(_SUPPLIER_FOLDER) == f'{_ROOT}/file_prices/{_SUPPLIER_FOLDER}'
    assert provider.result_folder() == f'{_ROOT}/file_prices/result'
    assert provider.log_folder() == f'{_ROOT}/logs'


def test_file_provider_detects_project_root() -> None:
    """без корня проект определяется по расположению модуля."""
    detected = FileConfigProvider().project_root
    assert Path(detected, 'parse_config').is_dir()
    assert FileConfigProvider(detected).project_root == detected


def test_fake_provider_paths_and_folders(tmp_path: Path) -> None:
    """FakeConfigProvider отдаёт пути внутри папки и создаёт их."""
    provider = FakeConfigProvider(tmp_path)
    assert provider.project_root == str(tmp_path)
    assert provider.config_file(_CONFIG_FILE) == str(tmp_path / 'parse_config' / _CONFIG_FILE)
    assert provider.price_folder(_SUPPLIER_FOLDER) == str(tmp_path / 'file_prices' / _SUPPLIER_FOLDER)
    assert Path(provider.result_folder()).is_dir()
    assert Path(provider.log_folder()).is_dir()


def test_fake_provider_reuses_existing_folders(tmp_path: Path) -> None:
    """повторный вызов на существующих папках не падает."""
    FakeConfigProvider(tmp_path)
    assert FakeConfigProvider(tmp_path).result_folder().endswith('result')


def test_log_paths_for_folder_dated_files() -> None:
    """LogPaths.for_folder кладёт сегодняшние файлы в папку логов."""
    paths = LogPaths.for_folder(_LOG_FOLDER)
    today = datetime.date.today()
    assert paths.folder == _LOG_FOLDER
    assert paths.log_file == f'{_LOG_FOLDER}/log_{today}.log'
    assert paths.err_file == f'{_LOG_FOLDER}/error_{today}.log'
