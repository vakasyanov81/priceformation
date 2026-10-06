"""Загрузка файлов настроек в parse_config."""

from pathlib import Path

import pytest

from cfg import init_cfg
from infrastructure.config.fake_config_provider import FakeConfigProvider
from infrastructure.config.file_config_provider import FileConfigProvider
from parsers.load_config import load_config
from parsers.load_config_errors import (
    ConfigFileNotFoundError,
    InvalidConfigJsonError,
    InvalidConfigKindError,
)

_JSON_TEXT = '{"ok": true}'
_XLSX_BYTES = b'xlsx-content'
_BLACK_LIST_TEXT = 'exact title\n*mask*\n'


@pytest.fixture
def config_root(fake_config_provider: FakeConfigProvider) -> Path:
    return Path(fake_config_provider.config_file(''))


def _write_source(tmp_path: Path, name: str, file_bytes: bytes) -> Path:
    source = tmp_path / 'incoming' / name
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_bytes(file_bytes)
    return source


def _write_folder(tmp_path: Path, files: dict[str, bytes]) -> Path:
    folder = tmp_path / 'incoming'
    folder.mkdir()
    for name, file_bytes in files.items():
        (folder / name).write_bytes(file_bytes)
    return folder


def _loaded(source: Path) -> Path:
    found = load_config(str(source))
    assert len(found) == 1
    return Path(found[0])


def test_load_json_moves(tmp_path: Path, config_root: Path) -> None:
    """json перемещается с исходным именем."""
    source = _write_source(tmp_path, 'vendor_list.json', _JSON_TEXT.encode())
    dest = _loaded(source)
    assert dest == config_root / 'vendor_list.json'
    assert dest.read_text(encoding='utf-8') == _JSON_TEXT
    assert not source.exists()


def test_load_json_rejects_invalid(tmp_path: Path, config_root: Path) -> None:
    """не JSON — исходник на месте, dest не пишется."""
    source = _write_source(tmp_path, 'vendor_list.json', b'not-json')
    with pytest.raises(InvalidConfigJsonError, match='JSON'):
        load_config(str(source))
    assert source.exists()
    assert not (config_root / 'vendor_list.json').exists()


def test_load_json_keeps_dest_on_invalid(tmp_path: Path, config_root: Path) -> None:
    """битый json не затирает существующий dest."""
    dest = config_root / 'markup_rules.json'
    dest.write_text(_JSON_TEXT, encoding='utf-8')
    source = _write_source(tmp_path, 'markup_rules.json', b'{')
    with pytest.raises(InvalidConfigJsonError):
        load_config(str(source))
    assert dest.read_text(encoding='utf-8') == _JSON_TEXT
    assert source.exists()


def test_load_json_array_ok(tmp_path: Path, config_root: Path) -> None:
    """любой валидный JSON, не только объект."""
    source = _write_source(tmp_path, 'title_aliases.json', b'[1, 2]')
    dest = _loaded(source)
    assert dest.read_text(encoding='utf-8') == '[1, 2]'
    assert dest == config_root / 'title_aliases.json'


def test_load_json_uppercase_suffix(tmp_path: Path, config_root: Path) -> None:
    """JSON → .json."""
    source = _write_source(tmp_path, 'vendor_list.JSON', _JSON_TEXT.encode())
    dest = _loaded(source)
    assert dest == config_root / 'vendor_list.json'
    assert dest.is_file()


def test_load_xlsx_moves(tmp_path: Path, config_root: Path) -> None:
    """xlsx перемещается как есть."""
    source = _write_source(tmp_path, 'correct-nomenclature.xlsx', _XLSX_BYTES)
    dest = _loaded(source)
    assert dest == config_root / 'correct-nomenclature.xlsx'
    assert dest.read_bytes() == _XLSX_BYTES
    assert not source.exists()


def test_load_xlsx_uppercase_suffix(tmp_path: Path, config_root: Path) -> None:
    """XLSX → .xlsx."""
    source = _write_source(tmp_path, 'correct-nomenclature.XLSX', _XLSX_BYTES)
    dest = _loaded(source)
    assert dest == config_root / 'correct-nomenclature.xlsx'


def test_load_xlsx_replaces(tmp_path: Path, config_root: Path) -> None:
    """существующий xlsx заменяется."""
    dest = config_root / 'correct-nomenclature.xlsx'
    dest.write_bytes(b'old')
    source = _write_source(tmp_path, 'correct-nomenclature.xlsx', _XLSX_BYTES)
    load_config(str(source))
    assert dest.read_bytes() == _XLSX_BYTES
    assert not source.exists()


def test_load_black_list_moves(tmp_path: Path, config_root: Path) -> None:
    """black_list без расширения."""
    source = _write_source(tmp_path, 'black_list', _BLACK_LIST_TEXT.encode())
    dest = _loaded(source)
    assert dest == config_root / 'black_list'
    assert dest.read_text(encoding='utf-8') == _BLACK_LIST_TEXT
    assert not source.exists()


def test_load_black_list_replaces(tmp_path: Path, config_root: Path) -> None:
    """существующий black_list заменяется."""
    dest = config_root / 'black_list'
    dest.write_text('old', encoding='utf-8')
    source = _write_source(tmp_path, 'black_list', _BLACK_LIST_TEXT.encode())
    load_config(str(source))
    assert dest.read_text(encoding='utf-8') == _BLACK_LIST_TEXT


def test_load_creates_config_folder(tmp_path: Path, config_root: Path) -> None:
    """parse_config создаётся."""
    source = _write_source(tmp_path, 'vendor_list.json', _JSON_TEXT.encode())
    load_config(str(source))
    assert config_root.is_dir()


def test_load_already_in_place(config_root: Path) -> None:
    """файл уже в parse_config — не трогаем."""
    dest = config_root / 'vendor_list.json'
    dest.write_text(_JSON_TEXT, encoding='utf-8')
    assert load_config(str(dest)) == [str(dest)]
    assert dest.read_text(encoding='utf-8') == _JSON_TEXT


def test_load_rejects_csv(tmp_path: Path, config_root: Path) -> None:
    """csv нельзя."""
    source = _write_source(tmp_path, 'a.csv', b'csv')
    with pytest.raises(InvalidConfigKindError, match='csv'):
        load_config(str(source))
    assert source.exists()


def test_load_rejects_xls(tmp_path: Path, config_root: Path) -> None:
    """xls нельзя, только xlsx."""
    source = _write_source(tmp_path, 'a.xls', b'xls')
    with pytest.raises(InvalidConfigKindError, match='xls'):
        load_config(str(source))


def test_load_rejects_black_list_txt(tmp_path: Path, config_root: Path) -> None:
    """black_list.txt нельзя."""
    source = _write_source(tmp_path, 'black_list.txt', b'a')
    with pytest.raises(InvalidConfigKindError, match=r'black_list\.txt'):
        load_config(str(source))


def test_load_missing_file(tmp_path: Path, config_root: Path) -> None:
    """нет файла."""
    missing = tmp_path / 'incoming' / 'gone.json'
    with pytest.raises(ConfigFileNotFoundError, match=r'gone\.json'):
        load_config(str(missing))


def test_load_missing_folder(tmp_path: Path, config_root: Path) -> None:
    """нет папки."""
    missing = tmp_path / 'incoming' / 'settings'
    with pytest.raises(ConfigFileNotFoundError, match='settings'):
        load_config(str(missing))


def test_load_empty_path(config_root: Path) -> None:
    """пустой путь."""
    with pytest.raises(ConfigFileNotFoundError, match='полный путь'):
        load_config('')


def test_load_folder_moves_allowed(tmp_path: Path, config_root: Path) -> None:
    """из папки переносятся json, xlsx и black_list."""
    folder = _write_folder(
        tmp_path,
        {
            'vendor_list.json': _JSON_TEXT.encode(),
            'correct-nomenclature.xlsx': _XLSX_BYTES,
            'black_list': _BLACK_LIST_TEXT.encode(),
        },
    )
    found = load_config(str(folder))
    dests = [
        config_root / 'black_list',
        config_root / 'correct-nomenclature.xlsx',
        config_root / 'vendor_list.json',
    ]
    assert found == [str(path) for path in dests]
    assert dests[0].read_text(encoding='utf-8') == _BLACK_LIST_TEXT
    assert dests[1].read_bytes() == _XLSX_BYTES
    assert dests[2].read_text(encoding='utf-8') == _JSON_TEXT
    assert list(folder.iterdir()) == []


def test_load_folder_rejects_unknown(tmp_path: Path, config_root: Path) -> None:
    """чужой файл в папке — ошибка, ничего не переносится."""
    folder = _write_folder(
        tmp_path,
        {
            'vendor_list.json': _JSON_TEXT.encode(),
            'notes.csv': b'csv',
        },
    )
    with pytest.raises(InvalidConfigKindError, match='csv'):
        load_config(str(folder))
    assert (folder / 'vendor_list.json').exists()
    assert (folder / 'notes.csv').exists()
    assert not (config_root / 'vendor_list.json').exists()


def test_load_folder_rejects_invalid_json(tmp_path: Path, config_root: Path) -> None:
    """битый json в папке — исходники на месте."""
    folder = _write_folder(
        tmp_path,
        {
            'vendor_list.json': _JSON_TEXT.encode(),
            'markup_rules.json': b'{',
        },
    )
    with pytest.raises(InvalidConfigJsonError):
        load_config(str(folder))
    assert (folder / 'vendor_list.json').exists()
    assert (folder / 'markup_rules.json').exists()
    assert not (config_root / 'vendor_list.json').exists()
    assert not (config_root / 'markup_rules.json').exists()


def test_load_folder_empty(tmp_path: Path, config_root: Path) -> None:
    """пустая папка."""
    folder = tmp_path / 'incoming'
    folder.mkdir()
    with pytest.raises(ConfigFileNotFoundError, match='нет файлов'):
        load_config(str(folder))


def test_load_folder_replaces(tmp_path: Path, config_root: Path) -> None:
    """файлы из папки заменяют существующие."""
    dest = config_root / 'vendor_list.json'
    dest.write_text('{}', encoding='utf-8')
    folder = _write_folder(tmp_path, {'vendor_list.json': _JSON_TEXT.encode()})
    load_config(str(folder))
    assert dest.read_text(encoding='utf-8') == _JSON_TEXT
    assert not (folder / 'vendor_list.json').exists()


def test_load_folder_skips_subdir(tmp_path: Path, config_root: Path) -> None:
    """вложенные папки не мешают переносу файлов."""
    folder = _write_folder(tmp_path, {'vendor_list.json': _JSON_TEXT.encode()})
    (folder / 'nested').mkdir()
    found = load_config(str(folder))
    assert found == [str(config_root / 'vendor_list.json')]
    assert (folder / 'nested').is_dir()


def test_load_json_binary(tmp_path: Path, config_root: Path) -> None:
    """не UTF-8 json."""
    source = _write_source(tmp_path, 'vendor_list.json', b'\xff\xfe{')
    with pytest.raises(InvalidConfigJsonError):
        load_config(str(source))
    assert source.exists()


def test_load_config_creates_nested_config_folder(tmp_path: Path) -> None:
    """parse_config создаётся вместе с промежуточными папками, а не требует готовой."""
    nested = tmp_path / 'deeply' / 'nested'
    init_cfg(FileConfigProvider(str(nested)))
    source = _write_source(tmp_path, 'vendor_list.json', _JSON_TEXT.encode('utf-8'))

    found = load_config(str(source))

    assert found == [str(nested / 'parse_config' / 'vendor_list.json')]
    assert (nested / 'parse_config' / 'vendor_list.json').is_file()


def test_load_vendor_config_to_vendors_subfolder(tmp_path: Path, config_root: Path) -> None:
    """Файл внутри vendors/ → parse_config/vendors/<filename>."""
    source = _write_source(tmp_path, 'vendors/stk.json', _JSON_TEXT.encode())
    dest = _loaded(source)
    assert dest == config_root / 'vendors' / 'stk.json'
    assert dest.read_text(encoding='utf-8') == _JSON_TEXT
    assert not source.exists()


def test_load_vendor_config_to_vendors_case_normalized(tmp_path: Path, config_root: Path) -> None:
    """.JSON → .json, vendors/ сохраняется."""
    source = _write_source(tmp_path, 'vendors/acme.JSON', _JSON_TEXT.encode())
    dest = _loaded(source)
    assert dest == config_root / 'vendors' / 'acme.json'


def test_load_vendor_config_respects_deep_vendors_path(tmp_path: Path, config_root: Path) -> None:
    """Глубокий путь с vendors/ — vendors/ сохраняется."""
    deep = tmp_path / 'a' / 'b' / 'vendors' / 'mim.json'
    deep.parent.mkdir(parents=True, exist_ok=True)
    deep.write_text(_JSON_TEXT, encoding='utf-8')
    dest = _loaded(deep)
    assert dest == config_root / 'vendors' / 'mim.json'


def test_flat_json_stays_flat(tmp_path: Path, config_root: Path) -> None:
    """Обычный файл без vendors/ — в корень parse_config."""
    source = _write_source(tmp_path, 'markup_rules.json', _JSON_TEXT.encode())
    dest = _loaded(source)
    assert dest == config_root / 'markup_rules.json'
