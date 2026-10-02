"""Провайдер путей окружения на процесс; подменяется в тестах через set_config_provider."""

from domain.protocols import ConfigProvider

_MSG_NOT_CONFIGURED = 'Config provider is not configured'


class ConfigProviderNotConfiguredError(RuntimeError):
    """Raised when get_config_provider runs before set_config_provider."""

    def __init__(self) -> None:
        super().__init__(_MSG_NOT_CONFIGURED)


class _CurrentConfigProvider:
    """Process-wide provider without a cfg import."""

    configured: ConfigProvider | None = None


def set_config_provider(provider: ConfigProvider) -> None:
    """Set paths used by data providers, price sources, writers and the .env lookup."""
    _CurrentConfigProvider.configured = provider


def get_config_provider() -> ConfigProvider:
    """Return the active provider; raise if init_cfg has not run."""
    provider = _CurrentConfigProvider.configured
    if provider is None:
        raise ConfigProviderNotConfiguredError()
    return provider
