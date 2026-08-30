"""tests for CommonPriceOut"""

from pathlib import Path
from typing import cast
from unittest.mock import MagicMock, patch

import pytest

from core.parse_paths import get_parse_paths
from parsers.common_price_output import CommonPriceOut, jsonl_output_files
from parsers.row_item.row_item import RowItem
from parsers.writer.jsonl_writer import RESULT_META_FILE
from parsers.writer.templates.all_templates import UnknownWriterTemplateError
from parsers.writer.templates.tmpl.for_doubles import ForDoubles
from parsers.writer.templates.tmpl.for_drom import ForDrom
from parsers.writer.xls_writer import XlsWriter
from parsers.writer.xwlt_driver import XlsxWriterDriver

_TITLE = "title"
_REPORT_PATH = "file_prices/result/doubles.xlsx"


def _result_folder() -> str:
    return get_parse_paths().result_folder


def test_nomenclature_title_correction() -> None:
    """корректирует title у каждой позиции"""
    row_old = RowItem({_TITLE: "old"})
    row_keep = RowItem({_TITLE: "keep"})
    out = CommonPriceOut(
        [row_old, row_keep],
        xls_writer=cast(type[XlsWriter], MagicMock),
        write_driver=cast(type[XlsxWriterDriver], MagicMock),
    )

    with patch(
        "parsers.common_price_output.get_nomenclature_corrected_title",
        side_effect=lambda title: f"fixed-{title}" if title == "old" else title,
    ):
        out.nomenclature_title_correction()

    assert row_old.title == "fixed-old"
    assert row_keep.title == "keep"


def test_write_all_prices() -> None:
    """write_all_prices корректирует названия и пишет по шаблонам"""
    rows = [RowItem({_TITLE: "t1"})]
    writer_cls = MagicMock()
    driver_cls = MagicMock()
    writer_instance = MagicMock()
    writer_instance.get_result_path.return_value = "file_prices/result/inner.xlsx"
    writer_cls.return_value = writer_instance
    driver_instance = MagicMock()
    driver_cls.return_value = driver_instance
    template = object()
    out = CommonPriceOut(
        rows,
        xls_writer=cast(type[XlsWriter], writer_cls),
        write_driver=cast(type[XlsxWriterDriver], driver_cls),
    )
    raw_rows = [{_TITLE: "t1"}]

    with (
        patch.object(out, "nomenclature_title_correction") as mock_corr,
        patch("parsers.common_price_output.all_writer_templates", return_value=[template]),
        patch(
            "parsers.common_price_output._to_raw_dicts",
            return_value=raw_rows,
        ) as mock_raw,
    ):
        written = out.write_all_prices()

    mock_corr.assert_called_once()
    mock_raw.assert_called_once_with(rows)
    driver_cls.assert_called_once_with()
    writer_cls.assert_called_once_with(
        driver_instance,
        raw_rows,
        template,
        result_folder=_result_folder(),
    )
    writer_instance.write.assert_called_once()
    assert written == ["file_prices/result/inner.xlsx"]


def test_write_all_prices_jsonl() -> None:
    """as_jsonl пишет jsonl и не трогает xlsx writer."""
    rows = [RowItem({_TITLE: "t1"})]
    writer_cls = MagicMock()
    driver_cls = MagicMock()
    template = object()
    out = CommonPriceOut(
        rows,
        xls_writer=cast(type[XlsWriter], writer_cls),
        write_driver=cast(type[XlsxWriterDriver], driver_cls),
    )
    raw_rows = [{_TITLE: "t1"}]
    jsonl_path = "file_prices/result/price.jsonl"

    with (
        patch.object(out, "nomenclature_title_correction") as mock_corr,
        patch("parsers.common_price_output.all_writer_templates", return_value=[template]),
        patch("parsers.common_price_output._to_raw_dicts", return_value=raw_rows),
        patch("parsers.common_price_output.write_template_jsonl", return_value=jsonl_path) as mock_jsonl,
    ):
        written = out.write_all_prices(as_jsonl=True)

    mock_corr.assert_called_once()
    writer_cls.assert_not_called()
    mock_jsonl.assert_called_once_with(raw_rows, template, _result_folder())
    assert written == jsonl_output_files([jsonl_path])


def test_write_all_prices_reloads_nomenclature() -> None:
    """второй write_all_prices в том же процессе видит новую карту номенклатуры"""
    row = RowItem({_TITLE: "old"})
    out = CommonPriceOut(
        [row],
        xls_writer=cast(type[XlsWriter], MagicMock),
        write_driver=cast(type[XlsxWriterDriver], MagicMock),
    )

    with (
        patch(
            "parsers.base_parser.nomenclature_correction.load_file",
            side_effect=[{"old": "A"}, {"old": "B"}],
        ),
        patch("parsers.common_price_output.all_writer_templates", return_value=[]),
    ):
        out.write_all_prices()
        assert row.title == "A"
        row.title = "old"
        out.write_all_prices()
        assert row.title == "B"


def test_write_doubles_report() -> None:
    """write_doubles_report пишет только размеченные дубли шаблоном ForDoubles"""
    double_row = RowItem({_TITLE: "dup"})
    double_row.is_double = True
    candidate = RowItem({_TITLE: "cand"})
    candidate.double_candidate = True
    unique = RowItem({_TITLE: "uniq"})
    rows = [double_row, candidate, unique]
    writer_cls = MagicMock()
    driver_cls = MagicMock()
    driver_instance = MagicMock()
    driver_cls.return_value = driver_instance
    writer_instance = MagicMock()
    writer_instance.get_result_path.return_value = _REPORT_PATH
    writer_cls.return_value = writer_instance
    out = CommonPriceOut(
        rows,
        xls_writer=cast(type[XlsWriter], writer_cls),
        write_driver=cast(type[XlsxWriterDriver], driver_cls),
    )
    raw_rows = [{_TITLE: "dup"}, {_TITLE: "cand"}]

    with (
        patch.object(out, "nomenclature_title_correction") as mock_corr,
        patch(
            "parsers.common_price_output._to_raw_dicts",
            return_value=raw_rows,
        ) as mock_raw,
    ):
        report_path = out.write_doubles_report()

    mock_corr.assert_not_called()
    mock_raw.assert_called_once_with([double_row, candidate])
    driver_cls.assert_called_once_with()
    writer_cls.assert_called_once_with(
        driver_instance,
        raw_rows,
        ForDoubles,
        result_folder=_result_folder(),
    )
    writer_instance.write.assert_called_once()
    assert report_path == _REPORT_PATH


def test_write_doubles_report_jsonl() -> None:
    """as_jsonl для дублей идёт в jsonl."""
    double_row = RowItem({_TITLE: "dup"})
    double_row.is_double = True
    out = CommonPriceOut(
        [double_row],
        xls_writer=cast(type[XlsWriter], MagicMock),
        write_driver=cast(type[XlsxWriterDriver], MagicMock),
    )
    jsonl_path = "file_prices/result/doubles.jsonl"
    raw_rows = [{_TITLE: "dup"}]

    with (
        patch("parsers.common_price_output._to_raw_dicts", return_value=raw_rows),
        patch("parsers.common_price_output.write_template_jsonl", return_value=jsonl_path) as mock_jsonl,
    ):
        report_path = out.write_doubles_report(as_jsonl=True)

    mock_jsonl.assert_called_once_with(raw_rows, ForDoubles, _result_folder())
    assert report_path == jsonl_path


def test_write_all_prices_single_template() -> None:
    """result_template пишет только выбранный шаблон."""
    writer_cls = MagicMock()
    driver_cls = MagicMock()
    writer_instance = MagicMock()
    writer_instance.get_result_path.return_value = "file_prices/result/drom.xlsx"
    writer_cls.return_value = writer_instance
    driver_instance = MagicMock()
    driver_cls.return_value = driver_instance
    out = CommonPriceOut(
        [RowItem({_TITLE: "t1"})],
        xls_writer=cast(type[XlsWriter], writer_cls),
        write_driver=cast(type[XlsxWriterDriver], driver_cls),
    )
    raw_rows = [{_TITLE: "t1"}]

    with (
        patch.object(out, "nomenclature_title_correction"),
        patch("parsers.common_price_output._to_raw_dicts", return_value=raw_rows),
    ):
        written = out.write_all_prices(result_template="for_drom")

    writer_cls.assert_called_once_with(
        driver_instance,
        raw_rows,
        ForDrom,
        result_folder=_result_folder(),
    )
    assert written == ["file_prices/result/drom.xlsx"]


def test_write_all_prices_unknown_template() -> None:
    """неизвестный шаблон — ошибка до записи."""
    writer_cls = MagicMock()
    out = CommonPriceOut(
        [],
        xls_writer=cast(type[XlsWriter], writer_cls),
        write_driver=cast(type[XlsxWriterDriver], MagicMock),
    )

    with pytest.raises(UnknownWriterTemplateError, match="nope"):
        out.write_all_prices(result_template="nope")

    writer_cls.assert_not_called()


def test_jsonl_output_files_appends_meta() -> None:
    """к jsonl добавляется result_meta.json из той же папки."""
    jsonl_path = "file_prices/result/price.jsonl"
    assert jsonl_output_files([jsonl_path]) == [
        jsonl_path,
        str(Path(jsonl_path).parent / RESULT_META_FILE),
    ]


def test_jsonl_output_files_empty() -> None:
    """без jsonl мета не добавляется."""
    assert not jsonl_output_files([])


def test_jsonl_output_files_skips_duplicate_meta() -> None:
    """повторно мета не дописывается."""
    jsonl_path = "file_prices/result/price.jsonl"
    once = jsonl_output_files([jsonl_path])
    assert jsonl_output_files(once) == once
