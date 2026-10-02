"""Очистка папки result."""

from pathlib import Path

from core.parse_paths import clear_result_folder
from infrastructure.config.fake_config_provider import FakeConfigProvider


def test_clear_result_folder_removes_contents(tmp_path: Path, fake_config_provider: FakeConfigProvider) -> None:
    """файлы и подпапки удаляются, сама result остаётся."""
    result_dir = Path(fake_config_provider.result_folder())
    (result_dir / 'old.xlsx').write_text('x', encoding='utf-8')
    nested = result_dir / 'nested'
    nested.mkdir()
    (nested / 'inner.jsonl').write_text('{}', encoding='utf-8')

    clear_result_folder()

    assert result_dir.is_dir()
    assert list(result_dir.iterdir()) == []


def test_clear_result_folder_missing_is_noop(fake_config_provider: FakeConfigProvider) -> None:
    """нет папки — ничего не делаем."""
    missing = Path(fake_config_provider.result_folder())
    missing.rmdir()

    clear_result_folder()

    assert not missing.exists()


def test_clear_result_folder_unlinks_symlink(tmp_path: Path, fake_config_provider: FakeConfigProvider) -> None:
    """симлинк удаляется, цель снаружи не трогаем."""
    result_dir = Path(fake_config_provider.result_folder())
    outside = tmp_path / 'keep.txt'
    outside.write_text('keep', encoding='utf-8')
    (result_dir / 'link.txt').symlink_to(outside)

    clear_result_folder()

    assert list(result_dir.iterdir()) == []
    assert outside.read_text(encoding='utf-8') == 'keep'
