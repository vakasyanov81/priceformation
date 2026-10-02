"""tests for the process-wide ConfigProvider holder"""

from collections.abc import Iterator
from pathlib import Path

import pytest

from domain.config_context import (
    ConfigProviderNotConfiguredError,
    _CurrentConfigProvider,
    get_config_provider,
    set_config_provider,
)
from infrastructure.config.fake_config_provider import FakeConfigProvider

_NOT_CONFIGURED = 'Config provider is not configured'


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
    with pytest.raises(ConfigProviderNotConfiguredError, match=_NOT_CONFIGURED):
        get_config_provider()


def test_config_provider_not_configured_error_message() -> None:
    """ConfigProviderNotConfiguredError содержит стандартное сообщение."""
    assert str(ConfigProviderNotConfiguredError()) == _NOT_CONFIGURED
