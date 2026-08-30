"""JSONL-запись по шаблону xlsx."""

import json
from pathlib import Path
from typing import Any, ClassVar

from parsers.row_item.row_item import RowItem
from parsers.writer.jsonl_writer import RESULT_META_FILE, write_template_jsonl
from parsers.writer.templates.iwrite_template import IWriteTemplate, WriteColumns
from parsers.writer.templates.tmpl.for_drom import ForDrom
from parsers.writer.templates.tmpl.for_inner import ForInner

from .fixtures import FixtureTemplate, write_data

_TITLE = "225/40R18 Crossleader 92Y"
_TYPE_NAME = "Тип товара"
_PRICE_NAME = "Цена"


class _SkipColumnTemplate(IWriteTemplate):
    """колонка skip не попадает в jsonl."""

    __COLUMNS__: ClassVar[WriteColumns] = [
        {"Номенклатура": {"field": RowItem.title.name}},
        {"Скрыто": {"field": RowItem.code.name, "skip": True}},
    ]
    __FILE__ = "skip_{now}.xlsx"


def _load_meta(folder: Path) -> dict[str, str]:
    loaded = json.loads((folder / RESULT_META_FILE).read_text(encoding="utf-8"))
    columns: dict[str, str] = {}
    for key, column_name in loaded.items():
        if not str(key).isdigit():
            continue
        columns[str(key)] = str(column_name)
    return columns


def _load_values(folder: Path) -> dict[str, Any]:
    loaded = json.loads((folder / RESULT_META_FILE).read_text(encoding="utf-8"))
    raw = loaded.get("values", {})
    assert isinstance(raw, dict)
    return raw


def _first_row(path: str) -> dict[str, Any]:
    text = Path(path).read_text(encoding="utf-8")
    loaded = json.loads(text.splitlines()[0])
    assert isinstance(loaded, dict)
    return loaded


def _meta_key(meta: dict[str, str], column: str) -> str:
    for key, name in meta.items():
        if name == column:
            return key
    raise AssertionError(column)


def test_write_template_jsonl_rows(tmp_path: Path) -> None:
    """каждая позиция — одна JSON-строка с компактными ключами."""
    path = write_template_jsonl(write_data, FixtureTemplate, str(tmp_path))
    assert path.endswith("default_result.jsonl")
    payload = _first_row(path)
    assert payload == {"1": _TITLE, "2": 3980.0, "3": 4.0}
    assert _load_meta(tmp_path) == {"1": "Номенклатура", "2": _PRICE_NAME, "3": "Остаток"}


def test_write_template_jsonl_inner_name(tmp_path: Path) -> None:
    """имя файла как у xlsx, расширение jsonl."""
    path = write_template_jsonl(write_data, ForInner, str(tmp_path))
    assert Path(path).suffix == ".jsonl"
    assert "price_" in Path(path).name


def test_jsonl_inner_compact_keys(tmp_path: Path) -> None:
    """inner: ключ 1 — тип товара, значения без имён колонок."""
    path = write_template_jsonl(write_data, ForInner, str(tmp_path))
    payload = _first_row(path)
    meta = _load_meta(tmp_path)
    assert meta["1"] == _TYPE_NAME
    assert payload["1"] == "Автошина"
    assert "Номенклатура" not in payload


def test_jsonl_shared_keys_across_templates(tmp_path: Path) -> None:
    """колонка с тем же именем получает тот же ключ во всех jsonl папки."""
    inner_path = write_template_jsonl(write_data, ForInner, str(tmp_path))
    drom_path = write_template_jsonl(write_data, ForDrom, str(tmp_path))
    meta = _load_meta(tmp_path)
    inner_row = _first_row(inner_path)
    drom_row = _first_row(drom_path)
    type_key = _meta_key(meta, _TYPE_NAME)
    price_key = _meta_key(meta, _PRICE_NAME)
    assert inner_row[type_key] == drom_row[type_key] == "Автошина"
    assert inner_row[price_key] == drom_row[price_key] == 3980.0
    assert meta["1"] == _TYPE_NAME


def test_jsonl_drom_skips_empty_rest(tmp_path: Path) -> None:
    """exclude шаблона drom отбрасывает пустой остаток."""
    empty_rest: dict[str, Any] = {**write_data[0], "rest_count": None}
    path = write_template_jsonl([empty_rest], ForDrom, str(tmp_path))
    assert Path(path).read_text(encoding="utf-8") == ""
    assert _load_meta(tmp_path)["1"] == _TYPE_NAME


def test_jsonl_skips_skip_columns(tmp_path: Path) -> None:
    """поле skip не пишется в объект и не попадает в мета."""
    path = write_template_jsonl(write_data, _SkipColumnTemplate, str(tmp_path))
    payload = _first_row(path)
    meta = _load_meta(tmp_path)
    assert payload == {"1": _TITLE}
    assert meta == {"1": "Номенклатура"}
    assert "Скрыто" not in meta.values()


def test_jsonl_omits_null_columns(tmp_path: Path) -> None:
    """колонка с null не пишется в строку, в мета остаётся."""
    row = {**write_data[0], "price_markup": None}
    path = write_template_jsonl([row], FixtureTemplate, str(tmp_path))
    assert _first_row(path) == {"1": _TITLE, "3": 4.0}
    assert _load_meta(tmp_path)["2"] == _PRICE_NAME


def test_jsonl_encodes_repeating_values(tmp_path: Path) -> None:
    """повторяющиеся строки кроме title заменяются на @N, числа нет."""
    other = {**write_data[0], "title": "other title"}
    path = write_template_jsonl([write_data[0], other], ForInner, str(tmp_path))
    meta = _load_meta(tmp_path)
    type_key = _meta_key(meta, _TYPE_NAME)
    price_key = _meta_key(meta, _PRICE_NAME)
    first_row = _first_row(path)
    assert first_row["1"] == "@1"
    assert first_row[type_key] == "@1"
    assert first_row[price_key] == 3980.0
    codebook = _load_values(tmp_path)
    assert codebook["@1"] == "Автошина"
    assert 3980.0 not in codebook.values()


def test_jsonl_keeps_unique_values(tmp_path: Path) -> None:
    """строка, встретившаяся один раз, не кодируется."""
    brand = RowItem.manufacturer.name
    first = {**write_data[0], brand: "BrandA"}
    second = {**write_data[0], "title": "other", brand: "BrandB"}
    path = write_template_jsonl([first, second], ForInner, str(tmp_path))
    brand_key = _meta_key(_load_meta(tmp_path), "Бренд")
    assert _first_row(path)[brand_key] == "BrandA"
    assert "BrandA" not in _load_values(tmp_path).values()


def test_jsonl_reuses_value_codes_across_files(tmp_path: Path) -> None:
    """один и тот же повтор в следующем jsonl получает тот же @N."""
    pair = [write_data[0], {**write_data[0], "title": "other"}]
    write_template_jsonl(pair, ForInner, str(tmp_path))
    drom_path = write_template_jsonl(pair, ForDrom, str(tmp_path))
    type_key = _meta_key(_load_meta(tmp_path), _TYPE_NAME)
    drom_row = _first_row(drom_path)
    codebook = _load_values(tmp_path)
    assert drom_row[type_key] == "@1"
    assert codebook["@1"] == "Автошина"
