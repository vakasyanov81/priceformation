"""tests for the composition root init_cfg"""

import datetime
from pathlib import Path

from cfg import init_cfg
from domain.config_context import get_config_provider
from infrastructure.config.fake_config_provider import FakeConfigProvider
from infrastructure.logging.json_mode import json_mode_active
from infrastructure.logging.log_paths import get_log_paths


def test_init_cfg_configures_log_paths() -> None:
    """init_cfg передаёт провайдер путей и логи в слои домена и инфраструктуры."""
    provider = init_cfg()
    log_folder = provider.log_folder()
    today = datetime.date.today()
    paths = get_log_paths()
    assert paths.folder == log_folder
    assert paths.log_file == f'{log_folder}/log_{today}.log'
    assert paths.err_file == f'{log_folder}/error_{today}.log'
    assert get_config_provider() is provider


def test_init_cfg_keeps_given_provider(tmp_path: Path) -> None:
    """переданный провайдер становится активным, файлы логов — в его папке."""
    previous = get_config_provider()
    provider = FakeConfigProvider(tmp_path)
    try:
        assert init_cfg(provider) is provider
        assert get_config_provider() is provider
        assert get_log_paths().folder == provider.log_folder()
    finally:
        init_cfg(previous)


def test_init_cfg_configures_logging() -> None:
    """init_cfg поднимает логирование, JSON-режим остаётся выключен."""
    init_cfg()
    assert not json_mode_active()
