"""tests for CommonPriceOut"""

from unittest.mock import MagicMock, patch

from parsers.common_price_output import CommonPriceOut
from parsers.row_item.row_item import RowItem

_TITLE = "title"


def test_nomenclature_title_correction() -> None:
    """корректирует title у каждой позиции"""
    row_old = RowItem({_TITLE: "old"})
    row_keep = RowItem({_TITLE: "keep"})
    out = CommonPriceOut([row_old, row_keep], xls_writer=MagicMock, write_driver=MagicMock)

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
    out = CommonPriceOut(rows, xls_writer=writer_cls, write_driver=driver_cls)
    raw_rows = [{_TITLE: "t1"}]

    with (
        patch.object(out, "nomenclature_title_correction") as mock_corr,
        patch("parsers.common_price_output.all_writer_templates", return_value=[template]),
        patch(
            "parsers.common_price_output.BaseParser.to_raw_dicts",
            return_value=raw_rows,
        ) as mock_raw,
    ):
        out.write_all_prices()

    mock_corr.assert_called_once()
    mock_raw.assert_called_once_with(rows)
    driver_cls.assert_called_once_with()
    writer_cls.assert_called_once_with(driver_instance, raw_rows, template)
