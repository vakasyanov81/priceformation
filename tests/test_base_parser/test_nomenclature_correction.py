"""tests for nomenclature title correction"""

from unittest.mock import MagicMock, patch

from parsers.base_parser import nomenclature_correction as noc

_CACHE_ATTR = "corrected_nomenclatures_"


def _clear_cache():
    """сброс кэша исправлений между тестами"""
    setattr(noc.get_nomenclature_corrected_title, _CACHE_ATTR, None)


def test_load_file_missing(tmp_path):
    """нет файла — пустой словарь"""
    with patch("parsers.base_parser.nomenclature_correction.MainConfig") as mock_cfg:
        mock_cfg.return_value.user_config_folder_path = str(tmp_path)
        assert not noc.load_file()


def test_load_file_reads_xlsx(tmp_path):
    """читает пары из Sheet1, пропуская заголовок"""
    (tmp_path / "correct-nomenclature.xlsx").write_bytes(b"placeholder")
    fake_sheet = MagicMock()
    fake_sheet.to_python.return_value = [
        ["vendor", "correct"],
        ["old title", "new title"],
        ["", "skip"],
        ["keep", "fixed"],
    ]
    fake_wb = MagicMock()
    fake_wb.get_sheet_by_name.return_value = fake_sheet

    with (
        patch("parsers.base_parser.nomenclature_correction.MainConfig") as mock_cfg,
        patch(
            "parsers.base_parser.nomenclature_correction.CalamineWorkbook.from_path",
            return_value=fake_wb,
        ),
    ):
        mock_cfg.return_value.user_config_folder_path = str(tmp_path)
        mapping = noc.load_file()
        assert mapping == {"old title": "new title", "keep": "fixed"}
        fake_wb.get_sheet_by_name.assert_called_once_with("Sheet1")


def test_corrected_title_cache():
    """подмена из кэша и fallback на исходный title"""
    _clear_cache()
    with patch.object(noc, "load_file", return_value={"A": "B"}) as mock_load:
        assert noc.get_nomenclature_corrected_title("A") == "B"
        assert noc.get_nomenclature_corrected_title("A") == "B"
        assert noc.get_nomenclature_corrected_title("C") == "C"
        mock_load.assert_called_once()
    _clear_cache()
