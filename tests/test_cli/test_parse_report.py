"""JSON-отчёт разбора прайса."""

import json
import time
from io import StringIO
from unittest.mock import patch

from parse_report import (
    REPORT_VERSION,
    dump_json,
    emit_json,
    empty_stats,
    error_payload,
    ok_payload,
)
from parse_report_build import (
    report_from_common,
    row_items_to_json,
    stats_from_common,
    warnings_from_common,
)
from parsers.common_price import CommonPrice
from parsers.row_item.row_item import RowItem

_TITLE = "шина test"
_OPT = 100
_MARKUP = 120
_ELAPSED = 1.234
_ROUNDED = 1.23
_RESULT_A = "file_prices/result/a.xlsx"
_RESULT_D = "file_prices/result/d.xlsx"
_SUV = "SUV"


def _priced_row() -> RowItem:
    return RowItem({"title": _TITLE, "price_opt": _OPT, "price_markup": _MARKUP})


def test_dump_json_roundtrip() -> None:
    """ok-отчёт сериализуется в JSON с ожидаемыми ключами."""
    payload = ok_payload(
        action="parse",
        positions=[{"title": _TITLE}],
        stats=empty_stats(0),
        warnings=[],
        files=[_RESULT_A],
        suppliers={"22": "Запаска"},
    )
    text = dump_json(payload)
    assert '"ok": true' in text
    assert payload["version"] == REPORT_VERSION
    assert payload["error"] is None


def test_error_payload_stable_keys() -> None:
    """ошибка заполняет ту же схему, ok=false."""
    payload = error_payload("parse", "RuntimeError", "boom")
    assert payload["ok"] is False
    assert payload["positions"] == []
    assert payload["disabled_suppliers"] == {}
    assert payload["error"] == {"kind": "RuntimeError", "message": "boom"}


def test_error_payload_compact() -> None:
    """compact — только ok/action/error."""
    payload = error_payload("load_supplier_prices", "OSError", "boom", compact=True)
    assert payload == {
        "ok": False,
        "action": "load_supplier_prices",
        "error": {"kind": "OSError", "message": "boom"},
    }


def test_emit_json_writes_stream() -> None:
    """emit_json печатает одну строку в поток."""
    stream = StringIO()
    emit_json(error_payload("zapaska", "OSError", "no net"), stream)
    assert stream.getvalue().endswith("\n")
    assert "no net" in stream.getvalue()


def test_emit_json_adds_elapsed() -> None:
    """started добавляет elapsed_seconds к ответу с ok."""
    stream = StringIO()
    emit_json({"ok": True, "action": "parse"}, stream, started=time.monotonic())
    payload = json.loads(stream.getvalue())
    assert payload["ok"] is True
    assert payload["action"] == "parse"
    assert payload["elapsed_seconds"] >= 0


def test_emit_json_skips_elapsed_without_ok() -> None:
    """каталог без ok не дополняется elapsed_seconds."""
    stream = StringIO()
    catalog = {"1": {"sup_code": "poshk"}}
    emit_json(catalog, stream, started=time.monotonic())
    assert json.loads(stream.getvalue()) == catalog


def test_row_items_include_parse_errors() -> None:
    """битое поле попадает в parse_errors."""
    row = RowItem({"price_opt": "not-a-number"})
    payload = row_items_to_json([row])[0]
    assert "parse_errors" in payload


def test_row_items_without_errors() -> None:
    """успешная строка без ключа parse_errors."""
    payload = row_items_to_json([_priced_row()])[0]
    assert payload["title"] == _TITLE
    assert "parse_errors" not in payload


def test_stats_and_warnings_from_common() -> None:
    """счётчики и тексты предупреждений из CommonPrice."""
    common = CommonPrice()
    row = _priced_row()
    row.is_double = True
    common.parsed_items.append(row)
    common.unknown_category_skips.append(("МИМ", _SUV))
    common.black_list_skips = 3
    stats = stats_from_common(common, _ELAPSED)
    assert stats["items"] == 1
    assert stats["priced_items"] == 1
    assert stats["doubles"] == 1
    assert stats["unknown_category_skips"] == 1
    assert stats["black_list_skips"] == 3
    assert stats["elapsed_seconds"] == _ROUNDED
    warnings = warnings_from_common(common)
    assert any(_SUV in message for message in warnings)
    assert any("black_list" in message for message in warnings)


def test_warnings_empty_without_skips() -> None:
    """без пропусков список предупреждений пуст."""
    assert warnings_from_common(CommonPrice()) == []


def test_empty_common_stats() -> None:
    """пустой разбор даёт нулевые счётчики."""
    stats = stats_from_common(CommonPrice(), 0)
    assert stats["items"] == 0
    assert stats["doubles"] == 0
    assert stats["priced_items"] == 0


def test_warnings_category_only() -> None:
    """только неизвестные категории."""
    common = CommonPrice()
    common.unknown_category_skips.append(("МИМ", _SUV))
    warnings = warnings_from_common(common)
    assert len(warnings) == 1
    assert _SUV in warnings[0]


def test_warnings_black_list_only() -> None:
    """только black_list."""
    common = CommonPrice()
    common.black_list_skips = 2
    warnings = warnings_from_common(common)
    assert len(warnings) == 1
    assert "black_list" in warnings[0]


def test_report_from_common_subset_rows() -> None:
    """rows= ограничивает positions, stats считаются по всему разбору."""
    common = CommonPrice()
    keep = _priced_row()
    keep.is_double = True
    skip = RowItem({"title": "other", "price_opt": _OPT, "price_markup": _MARKUP})
    common.parsed_items.extend([keep, skip])
    report = report_from_common("doubles", common, [_RESULT_D], 0.5, rows=[keep], all_result=True)
    assert report["ok"] is True
    assert report["action"] == "doubles"
    assert len(report["positions"]) == 1
    assert report["stats"]["items"] == 2
    assert report["files"] == [_RESULT_D]


def test_report_stats_only() -> None:
    """без all_result в JSON только статистика процесса."""
    common = CommonPrice()
    common.parsed_items.append(_priced_row())
    report = report_from_common("parse", common, [_RESULT_A], 0.4)
    assert report["positions"] == []
    assert report["stats"]["items"] == 1
    assert report["stats"]["elapsed_seconds"] == 0.4
    assert report["files"] == [_RESULT_A]


def test_report_splits_disabled_suppliers() -> None:
    """активные и отключённые поставщики — разные поля JSON."""
    common = CommonPrice()
    with patch(
        "parse_report_build.split_vendor_supplier_info",
        return_value=({"3": "Пионер"}, {"7": "STK"}),
    ):
        report = report_from_common("parse", common, [_RESULT_A], 0)
    assert report["suppliers"] == {"3": "Пионер"}
    assert report["disabled_suppliers"] == {"7": "STK"}
