"""tests for Mim sheet column maps."""

from parsers.row_item.row_item import RowItem
from parsers.vendors.mim.mim_2sheet import mim_sheet_2_params
from parsers.vendors.mim.mim_3sheet import mim_sheet_3_params


def test_sheet2_column_map() -> None:
    assert mim_sheet_2_params.columns == {
        0: RowItem.code.name,
        1: RowItem.title.name,
        3: RowItem.manufacturer.name,
        4: RowItem.model.name,
        6: RowItem.width.name,
        7: RowItem.height_percent.name,
        8: RowItem.construction_type.name,
        9: RowItem.diameter.name,
        11: RowItem.axis.name,
        12: RowItem.intimacy.name,
        13: RowItem.layering.name,
        14: RowItem.index_load.name,
        15: RowItem.index_velocity.name,
        20: RowItem.rest_count.name,
        22: RowItem.price_opt.name,
        23: RowItem.price_recommended.name,
    }


def test_sheet3_column_map() -> None:
    assert mim_sheet_3_params.columns == {
        0: RowItem.code.name,
        1: RowItem.title.name,
        3: RowItem.manufacturer.name,
        4: RowItem.model.name,
        6: RowItem.diameter.name,
        7: RowItem.width.name,
        8: RowItem.slot_count.name,
        9: RowItem.pcd1.name,
        11: RowItem.eet.name,
        12: RowItem.central_diameter.name,
        15: RowItem.disk_thickness.name,
        20: RowItem.rest_count.name,
        22: RowItem.price_opt.name,
        23: RowItem.price_recommended.name,
    }
