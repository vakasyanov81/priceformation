"""Очистка папки result."""

from collections.abc import Iterator
from pathlib import Path

import pytest

from core.parse_paths import ParsePaths, _CurrentParsePaths, clear_result_folder, configure_parse_paths

_FOLDER = "cfg"
_PRICES = "prices"


@pytest.fixture
def _restore_parse_paths() -> Iterator[None]:
    previous = _CurrentParsePaths.configured  # noqa: WPS437
    yield
    _CurrentParsePaths.configured = previous  # noqa: WPS437


def _configure(result_folder: Path) -> None:
    configure_parse_paths(
        ParsePaths(
            file_prices_folder=_PRICES,
            user_config_folder=_FOLDER,
            result_folder=str(result_folder),
        ),
    )


def test_clear_result_folder_removes_contents(tmp_path: Path, _restore_parse_paths: None) -> None:
    """файлы и подпапки удаляются, сама result остаётся."""
    result_dir = tmp_path / "result"
    result_dir.mkdir()
    (result_dir / "old.xlsx").write_text("x", encoding="utf-8")
    nested = result_dir / "nested"
    nested.mkdir()
    (nested / "inner.jsonl").write_text("{}", encoding="utf-8")
    _configure(result_dir)

    clear_result_folder()

    assert result_dir.is_dir()
    assert list(result_dir.iterdir()) == []


def test_clear_result_folder_missing_is_noop(tmp_path: Path, _restore_parse_paths: None) -> None:
    """нет папки — ничего не делаем."""
    missing = tmp_path / "absent"
    _configure(missing)
    clear_result_folder()
    assert not missing.exists()


def test_clear_result_folder_unlinks_symlink(tmp_path: Path, _restore_parse_paths: None) -> None:
    """симлинк удаляется, цель снаружи не трогаем."""
    result_dir = tmp_path / "result"
    result_dir.mkdir()
    outside = tmp_path / "keep.txt"
    outside.write_text("keep", encoding="utf-8")
    (result_dir / "link.txt").symlink_to(outside)
    _configure(result_dir)

    clear_result_folder()

    assert list(result_dir.iterdir()) == []
    assert outside.read_text(encoding="utf-8") == "keep"
