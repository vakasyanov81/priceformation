"""tests for parse_paths injection"""

from collections.abc import Iterator

import pytest

from core.parse_paths import (
    ParsePaths,
    _CurrentParsePaths,
    configure_parse_paths,
    get_parse_paths,
)

_FOLDER = "/var/parse_config"
_PRICES = "/var/file_prices"


@pytest.fixture
def _restore_parse_paths() -> Iterator[None]:
    previous = _CurrentParsePaths.configured  # noqa: WPS437
    yield
    _CurrentParsePaths.configured = previous  # noqa: WPS437


def test_configure_and_get_parse_paths(_restore_parse_paths: None) -> None:
    """configure_parse_paths сохраняет папки для get_parse_paths."""
    configure_parse_paths(ParsePaths(file_prices_folder=_PRICES, user_config_folder=_FOLDER))
    paths = get_parse_paths()
    assert paths.file_prices_folder == _PRICES
    assert paths.user_config_folder == _FOLDER
    assert paths.config_file("black_list") == f"{_FOLDER}/black_list"


def test_get_parse_paths_requires_configure(_restore_parse_paths: None) -> None:
    """без configure_parse_paths — явная ошибка."""
    _CurrentParsePaths.configured = None  # noqa: WPS437
    with pytest.raises(RuntimeError, match="Parse paths are not configured"):
        get_parse_paths()
