"""tests for nomenclature title correction"""

from typing import Any
from unittest.mock import MagicMock, patch

from core.parse_paths import ParsePaths
from parsers.base_parser import nomenclature_correction as noc

_NOMENCLATURE_FILE = "correct-nomenclature.xlsx"


def _clear_cache() -> None:
    """сброс кэша исправлений между тестами"""
    noc._NomenclatureCache.titles = None  # noqa: WPS437


def _paths(tmp_path: Any) -> ParsePaths:
    return ParsePaths(file_prices_folder=".", user_config_folder=str(tmp_path))


def test_load_file_missing(tmp_path: Any) -> None:
    """нет файла — пустой словарь"""
    with patch("parsers.base_parser.nomenclature_correction.get_parse_paths", return_value=_paths(tmp_path)):
        assert not noc.load_file()


def test_load_file_reads_xlsx(tmp_path: Any) -> None:
    """читает пары из Sheet1, пропуская заголовок"""
    (tmp_path / _NOMENCLATURE_FILE).write_bytes(b"placeholder")
    fake_sheet = MagicMock()
    fake_sheet.to_python.return_value = [
        ["vendor", "correct"],
        ["old title", "new title"],
        ["", "skip"],
        ["keep", "fixed"],
    ]
    fake_wb = MagicMock()
    fake_wb.get_sheet_by_name.return_value = fake_sheet
    expected_path = str(tmp_path / _NOMENCLATURE_FILE)

    with (
        patch("parsers.base_parser.nomenclature_correction.get_parse_paths", return_value=_paths(tmp_path)),
        patch(
            "parsers.base_parser.nomenclature_correction.CalamineWorkbook.from_path",
            return_value=fake_wb,
        ) as mock_from_path,
    ):
        mapping = noc.load_file()
        assert mapping == {"old title": "new title", "keep": "fixed"}
        fake_wb.get_sheet_by_name.assert_called_once_with("Sheet1")
        mock_from_path.assert_called_once_with(expected_path)


def test_corrected_title_cache() -> None:
    """подмена из кэша и fallback на исходный title"""
    _clear_cache()
    with patch.object(noc, "load_file", return_value={"A": "B"}) as mock_load:
        assert noc.get_nomenclature_corrected_title("A") == "B"
        assert noc.get_nomenclature_corrected_title("A") == "B"
        assert noc.get_nomenclature_corrected_title("C") == "C"
        mock_load.assert_called_once()
    _clear_cache()
