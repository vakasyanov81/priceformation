"""tests for the file system ConfigProvider implementations"""

from pathlib import Path

from infrastructure.config.fake_config_provider import FakeConfigProvider
from infrastructure.config.file_config_provider import FileConfigProvider

_ROOT = '/var/priceformation'
_CONFIG_FILE = 'vendor_list.json'
_SUPPLIER_FOLDER = 'poshk'


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
