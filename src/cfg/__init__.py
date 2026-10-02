"""Сборка конфигурации окружения: провайдер путей, файлы логов и логирование."""

from domain.config_context import set_config_provider
from domain.exception_log import set_exception_log_sink
from domain.protocols import ConfigProvider
from infrastructure.config.file_config_provider import FileConfigProvider
from infrastructure.logging.exception_logging import write_exception_log
from infrastructure.logging.log_paths import LogPaths, configure_log_paths
from infrastructure.logging.log_setup import setup_logging


def init_cfg(provider: ConfigProvider | None = None) -> ConfigProvider:
    """Настроить пути окружения и логи, вернуть активный ConfigProvider."""
    config_provider = FileConfigProvider() if provider is None else provider
    set_config_provider(config_provider)
    log_paths = LogPaths.for_folder(config_provider.log_folder())
    configure_log_paths(log_paths)
    setup_logging(log_paths)
    set_exception_log_sink(write_exception_log)
    return config_provider


__ALL__ = [init_cfg]
