"""
logic for zapaska (json) tire vendor
"""

from ..base_parser.base_parser_config import (
    ParseParamsSupplier,
    ParserParams,
    make_parse_config,
)
from ..base_parser.category_finder import canonical_product_type, raw_category_label
from ..row_item.row_item import RowItem
from .zapaska_disk_json import ZapaskaDiskJSON, column_mapping

column_mapping = dict(column_mapping)
column_mapping.update(
    {
        "height": RowItem.height_percent.name,
        "load_index": RowItem.index_load.name,
        "speed_index": RowItem.index_velocity.name,
        "studded": RowItem.spike.name,
    }
)

zapaska_tire_params = ParserParams(
    supplier=ParseParamsSupplier(folder_name="zapaska", name="Запаска (шины)", code="22"),
    start_row=0,
    sheet_info="",
    columns=column_mapping,
    stop_words=[],
    file_templates=["tire.json"],
    sheet_indexes=[],
    row_item_adaptor=RowItem,
)

zapaska_tire_config = make_parse_config(zapaska_tire_params)


class ZapaskaTireJSON(ZapaskaDiskJSON):
    """
    Parser rest and price opt for zapaska vendor
    """

    _type_production = "Шины"

    def category_for(self, row_item: RowItem) -> str | None:
        """Map supplier category onto the allowed product types."""
        resolved = canonical_product_type(row_item.type_production, self._category_finder)
        if resolved:
            return resolved
        self.unknown_category_skips.append(raw_category_label(row_item.type_production))
        return ""
