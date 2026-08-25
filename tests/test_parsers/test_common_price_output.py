"""tests for CommonPriceOut"""

from typing import cast
from unittest.mock import MagicMock, patch

from core.parse_paths import get_parse_paths
from parsers.common_price_output import CommonPriceOut
from parsers.row_item.row_item import RowItem
from parsers.writer.templates.tmpl.for_doubles import ForDoubles
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
        out.write_all_prices()

    mock_corr.assert_called_once()
    mock_raw.assert_called_once_with(rows)
    driver_cls.assert_called_once_with()
    writer_cls.assert_called_once_with(
        driver_instance,
        raw_rows,
        template,
        result_folder=_result_folder(),
    )
    writer_cls.return_value.write.assert_called_once()


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
