"""tests for JsonPriceReader column mapping and JSON shape."""

import json
from pathlib import Path
from typing import Any

import pytest

from parsers.json_reader import JsonPriceNotListError, JsonPriceReader, columns_from_params
from parsers.row_item.row_item import RowItem
from parsers.vendors.zapaska_disk_json import column_mapping as disk_columns
from parsers.vendors.zapaska_tire_json import zapaska_tire_params

_DISK_ROW = {"cae": "1", "price": 10}
_TIRE_ROW = {"cae": "1", "price": 10, "height": "80"}
_MISSING_FILE = "missing-price.json"
_SHEET_INDEXES: list[int] = []


def _write_json(tmp_path: Path, name: str, payload: object) -> str:
    price_file = tmp_path / name
    price_file.write_text(json.dumps(payload), encoding="utf-8")
    return str(price_file)


def _reader(file_path: str, columns: dict[Any, str]) -> JsonPriceReader:
    return JsonPriceReader.get_instance(file_path, {"columns": columns})


def test_json_price_reader_renames_disk_columns(tmp_path: Path) -> None:
    reader = _reader(_write_json(tmp_path, "disk.json", [_DISK_ROW]), disk_columns)
    rows = reader.parse()
    assert rows[0][RowItem.code_art.name] == "1"
    assert rows[0][RowItem.price_opt.name] == 10
    assert "cae" not in rows[0]
    assert "price" not in rows[0]


def test_json_price_reader_maps_tire_height(tmp_path: Path) -> None:
    tire_columns = zapaska_tire_params.columns
    reader = _reader(_write_json(tmp_path, "tire.json", [_TIRE_ROW]), tire_columns)
    rows = reader.parse()
    assert rows[0][RowItem.code_art.name] == "1"
    assert rows[0][RowItem.price_opt.name] == 10
    assert rows[0][RowItem.height_percent.name] == "80"
    assert "height" not in disk_columns


def test_json_price_reader_ignores_sheet_indexes(tmp_path: Path) -> None:
    reader = _reader(_write_json(tmp_path, "disk.json", [_DISK_ROW]), disk_columns)
    assert reader.parse(_SHEET_INDEXES) == reader.parse(None)


def test_json_price_reader_rejects_object_root(tmp_path: Path) -> None:
    reader = _reader(_write_json(tmp_path, "bad.json", {}), disk_columns)
    with pytest.raises(JsonPriceNotListError):
        reader.parse()


def test_json_price_reader_missing_file_raises() -> None:
    with pytest.raises(FileNotFoundError):
        JsonPriceReader.get_instance(_MISSING_FILE, {"columns": disk_columns})


def test_column_map_drops_int_keys() -> None:
    mapped = columns_from_params({"columns": {0: "title", "cae": "code_art"}})
    assert mapped == {"cae": "code_art"}
