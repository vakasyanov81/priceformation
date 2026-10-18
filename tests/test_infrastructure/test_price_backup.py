"""Копия папки прайсов перед обновлением."""

from pathlib import Path

import pytest

from infrastructure.data.price_backup import BACKUP_FOLDER_NAME, backup_prices, default_backup_folder


def test_default_backup_folder_in_system_temp(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """копия лежит во временной папке ОС под именем file_prices_old."""
    monkeypatch.setattr('tempfile.tempdir', str(tmp_path))

    assert default_backup_folder() == tmp_path / BACKUP_FOLDER_NAME


def test_backup_copies_tree_without_skipped_folder(tmp_path: Path) -> None:
    """поставщики копируются, result пропускается."""
    source = tmp_path / 'file_prices'
    (source / 'mim').mkdir(parents=True)
    (source / 'mim' / 'price.xlsx').write_text('new', encoding='utf-8')
    (source / 'result').mkdir()
    (source / 'result' / 'out.xlsx').write_text('x', encoding='utf-8')
    target = tmp_path / 'old'

    backup_prices(source, target, skip=source / 'result')

    assert (target / 'mim' / 'price.xlsx').read_text(encoding='utf-8') == 'new'
    assert not (target / 'result').exists()


def test_backup_replaces_previous_copy(tmp_path: Path) -> None:
    """старая копия не смешивается с новой."""
    source = tmp_path / 'file_prices'
    source.mkdir()
    target = tmp_path / 'old'
    target.mkdir()
    (target / 'stale.txt').write_text('stale', encoding='utf-8')

    backup_prices(source, target)

    assert list(target.iterdir()) == []


def test_backup_missing_source_gives_empty_copy(tmp_path: Path) -> None:
    """нет папки прайсов — пустая копия, без ошибки."""
    target = tmp_path / 'old'

    backup_prices(tmp_path / 'missing', target)

    assert target.is_dir()
