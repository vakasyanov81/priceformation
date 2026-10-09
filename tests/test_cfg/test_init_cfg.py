"""tests for the composition root init_cfg"""

import datetime
from pathlib import Path

import pytest

from cfg import init_cfg
from domain.config_context import get_config_provider
from infrastructure.config.fake_config_provider import FakeConfigProvider
from infrastructure.logging.exception_logging import write_exception_log
from infrastructure.logging.json_mode import json_mode_active
from infrastructure.logging.log_paths import LogPaths, get_log_paths


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


def test_init_cfg_passes_log_paths_to_setup_logging(monkeypatch: pytest.MonkeyPatch) -> None:
    """setup_logging получает вычисленные пути логов, а не None."""
    captured: list[LogPaths] = []
    monkeypatch.setattr('cfg.setup_logging', captured.append)

    provider = init_cfg()

    assert captured == [LogPaths.for_folder(provider.log_folder())]


def test_init_cfg_registers_exception_log_sink(monkeypatch: pytest.MonkeyPatch) -> None:
    """Приёмник сообщений об исключениях — боевая запись в лог, а не None."""
    captured: list[object] = []
    monkeypatch.setattr('cfg.set_exception_log_sink', captured.append)

    init_cfg()

    assert captured == [write_exception_log]
