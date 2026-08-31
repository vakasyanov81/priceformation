"""Загрузка файлов настроек в parse_config."""

from collections.abc import Iterator
from pathlib import Path

import pytest

from core.parse_paths import ParsePaths, _CurrentParsePaths, configure_parse_paths
from parsers.load_config import load_config
from parsers.load_config_errors import (
    ConfigFileNotFoundError,
    InvalidConfigJsonError,
    InvalidConfigKindError,
)

_JSON_TEXT = '{"ok": true}'
_XLSX_BYTES = b"xlsx-content"
_BLACK_LIST_TEXT = "exact title\n*mask*\n"


@pytest.fixture
def _restore_parse_paths() -> Iterator[None]:
    previous = _CurrentParsePaths.configured  # noqa: WPS437
    yield
    _CurrentParsePaths.configured = previous  # noqa: WPS437


@pytest.fixture
def config_root(tmp_path: Path, _restore_parse_paths: None) -> Path:
    config = tmp_path / "parse_config"
    configure_parse_paths(
        ParsePaths(
            file_prices_folder=str(tmp_path / "file_prices"),
            user_config_folder=str(config),
            result_folder=str(tmp_path / "result"),
        ),
    )
    return config


def _write_source(tmp_path: Path, name: str, file_bytes: bytes) -> Path:
    source = tmp_path / "incoming" / name
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_bytes(file_bytes)
    return source


def test_load_json_moves(tmp_path: Path, config_root: Path) -> None:
    """json перемещается с исходным именем."""
    source = _write_source(tmp_path, "vendor_list.json", _JSON_TEXT.encode())
    dest = Path(load_config(str(source)))
    assert dest == config_root / "vendor_list.json"
    assert dest.read_text(encoding="utf-8") == _JSON_TEXT
    assert not source.exists()


def test_load_json_rejects_invalid(tmp_path: Path, config_root: Path) -> None:
    """не JSON — исходник на месте, dest не пишется."""
    source = _write_source(tmp_path, "vendor_list.json", b"not-json")
    with pytest.raises(InvalidConfigJsonError, match="JSON"):
        load_config(str(source))
    assert source.exists()
    assert not (config_root / "vendor_list.json").exists()


def test_load_json_keeps_dest_on_invalid(tmp_path: Path, config_root: Path) -> None:
    """битый json не затирает существующий dest."""
    config_root.mkdir()
    dest = config_root / "markup_rules.json"
    dest.write_text(_JSON_TEXT, encoding="utf-8")
    source = _write_source(tmp_path, "markup_rules.json", b"{")
    with pytest.raises(InvalidConfigJsonError):
        load_config(str(source))
    assert dest.read_text(encoding="utf-8") == _JSON_TEXT
    assert source.exists()


def test_load_json_array_ok(tmp_path: Path, config_root: Path) -> None:
    """любой валидный JSON, не только объект."""
    source = _write_source(tmp_path, "title_aliases.json", b"[1, 2]")
    dest = Path(load_config(str(source)))
    assert dest.read_text(encoding="utf-8") == "[1, 2]"
    assert dest == config_root / "title_aliases.json"


def test_load_json_uppercase_suffix(tmp_path: Path, config_root: Path) -> None:
    """JSON → .json."""
    source = _write_source(tmp_path, "vendor_list.JSON", _JSON_TEXT.encode())
    dest = Path(load_config(str(source)))
    assert dest == config_root / "vendor_list.json"
    assert dest.is_file()


def test_load_xlsx_moves(tmp_path: Path, config_root: Path) -> None:
    """xlsx перемещается как есть."""
    source = _write_source(tmp_path, "correct-nomenclature.xlsx", _XLSX_BYTES)
    dest = Path(load_config(str(source)))
    assert dest == config_root / "correct-nomenclature.xlsx"
    assert dest.read_bytes() == _XLSX_BYTES
    assert not source.exists()


def test_load_xlsx_uppercase_suffix(tmp_path: Path, config_root: Path) -> None:
    """XLSX → .xlsx."""
    source = _write_source(tmp_path, "correct-nomenclature.XLSX", _XLSX_BYTES)
    dest = Path(load_config(str(source)))
    assert dest == config_root / "correct-nomenclature.xlsx"


def test_load_xlsx_replaces(tmp_path: Path, config_root: Path) -> None:
    """существующий xlsx заменяется."""
    config_root.mkdir()
    dest = config_root / "correct-nomenclature.xlsx"
    dest.write_bytes(b"old")
    source = _write_source(tmp_path, "correct-nomenclature.xlsx", _XLSX_BYTES)
    load_config(str(source))
    assert dest.read_bytes() == _XLSX_BYTES
    assert not source.exists()


def test_load_black_list_moves(tmp_path: Path, config_root: Path) -> None:
    """black_list без расширения."""
    source = _write_source(tmp_path, "black_list", _BLACK_LIST_TEXT.encode())
    dest = Path(load_config(str(source)))
    assert dest == config_root / "black_list"
    assert dest.read_text(encoding="utf-8") == _BLACK_LIST_TEXT
    assert not source.exists()


def test_load_black_list_replaces(tmp_path: Path, config_root: Path) -> None:
    """существующий black_list заменяется."""
    config_root.mkdir()
    dest = config_root / "black_list"
    dest.write_text("old", encoding="utf-8")
    source = _write_source(tmp_path, "black_list", _BLACK_LIST_TEXT.encode())
    load_config(str(source))
    assert dest.read_text(encoding="utf-8") == _BLACK_LIST_TEXT


def test_load_creates_config_folder(tmp_path: Path, config_root: Path) -> None:
    """parse_config создаётся."""
    source = _write_source(tmp_path, "vendor_list.json", _JSON_TEXT.encode())
    load_config(str(source))
    assert config_root.is_dir()


def test_load_already_in_place(config_root: Path) -> None:
    """файл уже в parse_config — не трогаем."""
    config_root.mkdir()
    dest = config_root / "vendor_list.json"
    dest.write_text(_JSON_TEXT, encoding="utf-8")
    assert load_config(str(dest)) == str(dest)
    assert dest.read_text(encoding="utf-8") == _JSON_TEXT


def test_load_rejects_csv(tmp_path: Path, config_root: Path) -> None:
    """csv нельзя."""
    source = _write_source(tmp_path, "a.csv", b"csv")
    with pytest.raises(InvalidConfigKindError, match="csv"):
        load_config(str(source))
    assert source.exists()


def test_load_rejects_xls(tmp_path: Path, config_root: Path) -> None:
    """xls нельзя, только xlsx."""
    source = _write_source(tmp_path, "a.xls", b"xls")
    with pytest.raises(InvalidConfigKindError, match="xls"):
        load_config(str(source))


def test_load_rejects_black_list_txt(tmp_path: Path, config_root: Path) -> None:
    """black_list.txt нельзя."""
    source = _write_source(tmp_path, "black_list.txt", b"a")
    with pytest.raises(InvalidConfigKindError, match=r"black_list\.txt"):
        load_config(str(source))


def test_load_missing_file(tmp_path: Path, config_root: Path) -> None:
    """нет файла."""
    missing = tmp_path / "incoming" / "gone.json"
    with pytest.raises(ConfigFileNotFoundError, match=r"gone\.json"):
        load_config(str(missing))


def test_load_empty_path(config_root: Path) -> None:
    """пустой путь."""
    with pytest.raises(ConfigFileNotFoundError, match="полный путь"):
        load_config("")


def test_load_json_binary(tmp_path: Path, config_root: Path) -> None:
    """не UTF-8 json."""
    source = _write_source(tmp_path, "vendor_list.json", b"\xff\xfe{")
    with pytest.raises(InvalidConfigJsonError):
        load_config(str(source))
    assert source.exists()
