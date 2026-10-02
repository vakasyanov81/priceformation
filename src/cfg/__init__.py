"""Сборка конфигурации окружения: провайдер путей и файлы логов."""

from core.config_provider import set_config_provider
from core.log_paths import LogPaths, configure_log_paths
from domain.protocols import ConfigProvider
from infrastructure.config.file_config_provider import FileConfigProvider


def init_cfg(provider: ConfigProvider | None = None) -> ConfigProvider:
    """Настроить пути окружения и логи, вернуть активный ConfigProvider."""
    config_provider = FileConfigProvider() if provider is None else provider
    set_config_provider(config_provider)
    configure_log_paths(LogPaths.for_folder(config_provider.log_folder()))
    return config_provider


__ALL__ = [init_cfg]
