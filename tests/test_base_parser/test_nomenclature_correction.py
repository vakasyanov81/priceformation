"""tests for nomenclature title correction"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from python_calamine import WorksheetNotFound

from infrastructure.config.fake_config_provider import FakeConfigProvider
from parsers.base_parser import nomenclature_correction as noc

_NOMENCLATURE_FILE = 'correct-nomenclature.xlsx'


def _write_nomenclature(fake_config_provider: FakeConfigProvider, file_bytes: bytes) -> str:
    file_path = fake_config_provider.config_file(_NOMENCLATURE_FILE)
    Path(file_path).write_bytes(file_bytes)
    return file_path


def test_load_file_missing(fake_config_provider: FakeConfigProvider) -> None:
    """нет файла — пустой словарь"""
    assert not noc.load_file()


def test_load_file_reads_xlsx(fake_config_provider: FakeConfigProvider) -> None:
    """читает пары из Sheet1, пропуская заголовок"""
    expected_path = _write_nomenclature(fake_config_provider, b'placeholder')
    fake_sheet = MagicMock()
    fake_sheet.to_python.return_value = [
        ['vendor', 'correct'],
        ['old title', 'new title'],
        ['', 'skip'],
        ['keep', 'fixed'],
    ]
    fake_wb = MagicMock()
    fake_wb.get_sheet_by_name.return_value = fake_sheet

    with (
        patch(
            'parsers.base_parser.nomenclature_correction.CalamineWorkbook.from_path',
            return_value=fake_wb,
        ) as mock_from_path,
    ):
        mapping = noc.load_file()
        assert mapping == {'old title': 'new title', 'keep': 'fixed'}
        fake_wb.get_sheet_by_name.assert_called_once_with('Sheet1')
        mock_from_path.assert_called_once_with(expected_path)


def test_corrected_title_cache() -> None:
    """подмена из кэша и fallback на исходный title"""
    noc.clear_nomenclature_cache()
    with patch.object(noc, 'load_file', return_value={'A': 'B'}) as mock_load:
        assert noc.get_nomenclature_corrected_title('A') == 'B'
        assert noc.get_nomenclature_corrected_title('A') == 'B'
        assert noc.get_nomenclature_corrected_title('C') == 'C'
        mock_load.assert_called_once()
    noc.clear_nomenclature_cache()


def test_invalid_file_raises_error(fake_config_provider: FakeConfigProvider) -> None:
    """битый xlsx — CalamineError/ZipError обёрнуты в NomenclatureCorrectionFileError"""
    _write_nomenclature(fake_config_provider, b'garbage')
    with (
        pytest.raises(
            noc.NomenclatureCorrectionFileError,
            match=r'correct-nomenclature\.xlsx повреждён',
        ),
    ):
        noc.load_file()


def test_missing_sheet_raises_error(fake_config_provider: FakeConfigProvider) -> None:
    """нет листа Sheet1 — WorksheetNotFound обёрнут в NomenclatureCorrectionFileError"""
    _write_nomenclature(fake_config_provider, b'placeholder')
    fake_wb = MagicMock()
    fake_wb.get_sheet_by_name.side_effect = WorksheetNotFound('Sheet1')
    fake_wb.sheet_names = ['OtherSheet']
    with (
        patch(
            'parsers.base_parser.nomenclature_correction.CalamineWorkbook.from_path',
            return_value=fake_wb,
        ),
        pytest.raises(
            noc.NomenclatureCorrectionFileError,
            match=r'correct-nomenclature\.xlsx повреждён',
        ),
    ):
        noc.load_file()


def test_too_few_columns_raises_error(fake_config_provider: FakeConfigProvider) -> None:
    """строка с одной колонкой — IndexError обёрнут в NomenclatureCorrectionFileError"""
    _write_nomenclature(fake_config_provider, b'placeholder')
    fake_sheet = MagicMock()
    fake_sheet.to_python.return_value = [
        ['vendor'],
        ['old title'],
    ]
    fake_wb = MagicMock()
    fake_wb.get_sheet_by_name.return_value = fake_sheet
    with (
        patch(
            'parsers.base_parser.nomenclature_correction.CalamineWorkbook.from_path',
            return_value=fake_wb,
        ),
        pytest.raises(
            noc.NomenclatureCorrectionFileError,
            match=r'correct-nomenclature\.xlsx повреждён',
        ),
    ):
        noc.load_file()


def test_corrected_title_reloads_after_clear() -> None:
    """после сброса кэша повторный вызов читает новую карту"""
    noc.clear_nomenclature_cache()
    maps = [{'A': 'B'}, {'A': 'C'}]
    with patch.object(noc, 'load_file', side_effect=maps) as mock_load:
        assert noc.get_nomenclature_corrected_title('A') == 'B'
        assert noc.get_nomenclature_corrected_title('A') == 'B'
        noc.clear_nomenclature_cache()
        assert noc.get_nomenclature_corrected_title('A') == 'C'
        assert mock_load.call_count == 2
    noc.clear_nomenclature_cache()
