"""tests for nomenclature title correction"""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from python_calamine import WorksheetNotFound

from core.parse_paths import ParsePaths
from parsers.base_parser import nomenclature_correction as noc

_NOMENCLATURE_FILE = 'correct-nomenclature.xlsx'


def _paths(tmp_path: Any) -> ParsePaths:
    return ParsePaths(file_prices_folder='.', user_config_folder=str(tmp_path), result_folder='.')


def test_load_file_missing(tmp_path: Any) -> None:
    """нет файла — пустой словарь"""
    with patch('parsers.base_parser.nomenclature_correction.get_parse_paths', return_value=_paths(tmp_path)):
        assert not noc.load_file()


def test_load_file_reads_xlsx(tmp_path: Any) -> None:
    """читает пары из Sheet1, пропуская заголовок"""
    (tmp_path / _NOMENCLATURE_FILE).write_bytes(b'placeholder')
    fake_sheet = MagicMock()
    fake_sheet.to_python.return_value = [
        ['vendor', 'correct'],
        ['old title', 'new title'],
        ['', 'skip'],
        ['keep', 'fixed'],
    ]
    fake_wb = MagicMock()
    fake_wb.get_sheet_by_name.return_value = fake_sheet
    expected_path = str(tmp_path / _NOMENCLATURE_FILE)

    with (
        patch('parsers.base_parser.nomenclature_correction.get_parse_paths', return_value=_paths(tmp_path)),
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


def test_invalid_file_raises_error(tmp_path: Any) -> None:
    """битый xlsx — CalamineError/ZipError обёрнуты в NomenclatureCorrectionFileError"""
    (tmp_path / _NOMENCLATURE_FILE).write_bytes(b'garbage')
    with (
        patch('parsers.base_parser.nomenclature_correction.get_parse_paths', return_value=_paths(tmp_path)),
        patch.object(noc, 'err_msg'),
        pytest.raises(
            noc.NomenclatureCorrectionFileError,
            match=r'correct-nomenclature\.xlsx повреждён',
        ),
    ):
        noc.load_file()


def test_missing_sheet_raises_error(tmp_path: Any) -> None:
    """нет листа Sheet1 — WorksheetNotFound обёрнут в NomenclatureCorrectionFileError"""
    (tmp_path / _NOMENCLATURE_FILE).write_bytes(b'placeholder')
    fake_wb = MagicMock()
    fake_wb.get_sheet_by_name.side_effect = WorksheetNotFound('Sheet1')
    fake_wb.sheet_names = ['OtherSheet']
    with (
        patch('parsers.base_parser.nomenclature_correction.get_parse_paths', return_value=_paths(tmp_path)),
        patch(
            'parsers.base_parser.nomenclature_correction.CalamineWorkbook.from_path',
            return_value=fake_wb,
        ),
        patch.object(noc, 'err_msg'),
        pytest.raises(
            noc.NomenclatureCorrectionFileError,
            match=r'correct-nomenclature\.xlsx повреждён',
        ),
    ):
        noc.load_file()


def test_too_few_columns_raises_error(tmp_path: Any) -> None:
    """строка с одной колонкой — IndexError обёрнут в NomenclatureCorrectionFileError"""
    (tmp_path / _NOMENCLATURE_FILE).write_bytes(b'placeholder')
    fake_sheet = MagicMock()
    fake_sheet.to_python.return_value = [
        ['vendor'],
        ['old title'],
    ]
    fake_wb = MagicMock()
    fake_wb.get_sheet_by_name.return_value = fake_sheet
    with (
        patch('parsers.base_parser.nomenclature_correction.get_parse_paths', return_value=_paths(tmp_path)),
        patch(
            'parsers.base_parser.nomenclature_correction.CalamineWorkbook.from_path',
            return_value=fake_wb,
        ),
        patch.object(noc, 'err_msg'),
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
