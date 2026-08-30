"""JSON-режим CLI."""

import json
from unittest.mock import MagicMock, patch

import pytest

from core.log_message import print_log
from parsers.row_item.row_item import RowItem
from run_argv import DOUBLES, PARSE, ZAPASKA
from run_machine import machine_json

_TITLE = "шина"
_PATH = "file_prices/result/price.jsonl"
_DOUBLE_PATH = "file_prices/result/doubles.jsonl"
_PRICE_FIELDS = {"title": _TITLE, "price_opt": 10, "price_markup": 12}
_COMMON_PRICE = "run_machine.CommonPrice"
_ALL_VENDORS = "run_machine.all_vendors"
_PRICE_OUT = "run_machine.CommonPriceOut"
_LOG_NOISE = "NOISE-ON-STDOUT"


def _common_with_row() -> MagicMock:
    row = RowItem(_PRICE_FIELDS)
    common = MagicMock()
    common.parsed_items = [row]
    common.unknown_category_skips = []
    common.black_list_skips = 0
    return common


def _mark_common(rows: list[RowItem]) -> MagicMock:
    common = MagicMock()
    common.parsed_items = rows
    common.unknown_category_skips = []
    common.black_list_skips = 0
    return common


def test_json_parse_success(capsys: pytest.CaptureFixture[str]) -> None:
    """parse --json без --all-result: статистика процесса, без позиций."""
    common = _common_with_row()
    with (
        patch(_COMMON_PRICE, return_value=common),
        patch(_ALL_VENDORS, return_value=[]),
        patch(_PRICE_OUT) as mock_out,
    ):
        mock_out.return_value.write_all_prices.return_value = [_PATH]
        code = machine_json(PARSE)
    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    assert payload["ok"] is True
    assert payload["action"] == PARSE
    assert payload["positions"] == []
    assert payload["stats"]["items"] == 1
    assert payload["files"] == [_PATH]
    mock_out.return_value.write_all_prices.assert_called_once_with(as_jsonl=True)


def test_json_stdout_is_only_json(capsys: pytest.CaptureFixture[str]) -> None:
    """логи разбора не попадают в stdout и stderr."""
    common = _common_with_row()
    common.parse_all_vendors.side_effect = lambda _vendors: print_log(_LOG_NOISE)
    with (
        patch(_COMMON_PRICE, return_value=common),
        patch(_ALL_VENDORS, return_value=[]),
        patch(_PRICE_OUT) as mock_out,
    ):
        mock_out.return_value.write_all_prices.return_value = [_PATH]
        machine_json(PARSE)
    captured = capsys.readouterr()
    assert _LOG_NOISE not in captured.out
    assert _LOG_NOISE not in captured.err
    json.loads(captured.out)


def test_json_parse_all_result(capsys: pytest.CaptureFixture[str]) -> None:
    """parse --all-result: позиции в JSON."""
    common = _common_with_row()
    with (
        patch(_COMMON_PRICE, return_value=common),
        patch(_ALL_VENDORS, return_value=[]),
        patch(_PRICE_OUT) as mock_out,
    ):
        mock_out.return_value.write_all_prices.return_value = [_PATH]
        code = machine_json(PARSE, all_result=True)
    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    assert payload["positions"][0]["title"] == _TITLE
    assert payload["stats"]["items"] == 1


def test_json_parse_error(capsys: pytest.CaptureFixture[str]) -> None:
    """исключение разбора → JSON с ok=false и код 1."""
    with patch(_COMMON_PRICE, side_effect=RuntimeError("boom")):
        code = machine_json(PARSE)
    payload = json.loads(capsys.readouterr().out)
    assert code == 1
    assert payload["ok"] is False
    assert payload["error"]["kind"] == "RuntimeError"
    assert payload["error"]["message"] == "boom"


def test_json_keyboard_interrupt(capsys: pytest.CaptureFixture[str]) -> None:
    """KeyboardInterrupt → JSON-ошибка, код 1."""
    with patch(_COMMON_PRICE, side_effect=KeyboardInterrupt):
        code = machine_json(PARSE)
    payload = json.loads(capsys.readouterr().out)
    assert code == 1
    assert payload["error"]["kind"] == "KeyboardInterrupt"


def test_json_doubles(capsys: pytest.CaptureFixture[str]) -> None:
    """doubles --json без --all-result: статистика, без позиций."""
    double_row = RowItem({"title": "dup", "price_opt": 1, "price_markup": 2})
    double_row.is_double = True
    unique = RowItem({"title": "uniq", "price_opt": 1, "price_markup": 2})
    common = _mark_common([double_row, unique])
    with (
        patch(_COMMON_PRICE, return_value=common),
        patch(_ALL_VENDORS, return_value=[]),
        patch(_PRICE_OUT) as mock_out,
    ):
        mock_out.return_value.write_doubles_report.return_value = _DOUBLE_PATH
        code = machine_json(DOUBLES)
    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    assert payload["action"] == DOUBLES
    assert payload["positions"] == []
    assert payload["stats"]["doubles"] == 1
    assert payload["files"] == [_DOUBLE_PATH]
    mock_out.return_value.write_doubles_report.assert_called_once_with(as_jsonl=True)


def test_json_doubles_all_result(capsys: pytest.CaptureFixture[str]) -> None:
    """doubles --all-result отдаёт только дубли."""
    double_row = RowItem({"title": "dup", "price_opt": 1, "price_markup": 2})
    double_row.is_double = True
    candidate = RowItem({"title": "cand", "price_opt": 1, "price_markup": 2})
    candidate.double_candidate = True
    unique = RowItem({"title": "uniq", "price_opt": 1, "price_markup": 2})
    common = _mark_common([double_row, candidate, unique])
    with (
        patch(_COMMON_PRICE, return_value=common),
        patch(_ALL_VENDORS, return_value=[]),
        patch(_PRICE_OUT) as mock_out,
    ):
        mock_out.return_value.write_doubles_report.return_value = _DOUBLE_PATH
        code = machine_json(DOUBLES, all_result=True)
    payload = json.loads(capsys.readouterr().out)
    titles = {position["title"] for position in payload["positions"]}
    assert code == 0
    assert titles == {"dup", "cand"}
    assert payload["files"] == [_DOUBLE_PATH]


def test_json_unknown_command(capsys: pytest.CaptureFixture[str]) -> None:
    """неизвестная команда → JSON-ошибка."""
    code = machine_json("nope")
    payload = json.loads(capsys.readouterr().out)
    assert code == 1
    assert payload["ok"] is False
    assert payload["error"]["kind"] == "KeyError"


def test_json_zapaska(capsys: pytest.CaptureFixture[str]) -> None:
    """zapaska --json без позиций, код 0."""
    with (
        patch("run_machine.get_zapaska_api_config", return_value=MagicMock()),
        patch("run_machine.load_remote_vendor_data") as mock_load,
    ):
        code = machine_json(ZAPASKA)
        payload = json.loads(capsys.readouterr().out)
        assert code == 0
        assert payload["ok"] is True
        assert payload["action"] == ZAPASKA
        assert payload["positions"] == []
        mock_load.assert_called_once()
