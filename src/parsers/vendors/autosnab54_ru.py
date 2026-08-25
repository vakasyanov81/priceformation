"""
logic for autosnab54_ru vendor
"""

from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.base_parser_config import (
    ParseParamsSupplier,
    ParserParams,
    make_parse_config,
)
from parsers.row_item.row_item import RowItem
from parsers.vendors.autosnab_title import fill_from_title

autosnab_params = ParserParams(
    supplier=ParseParamsSupplier(folder_name="autosnab54_ru", name="Автоснабжение", code="6"),
    start_row=2,
    sheet_info="",
    columns={
        0: RowItem.type_production.name,
        1: RowItem.manufacturer.name,
        2: RowItem.title.name,
        3: RowItem.season.name,
        4: RowItem.spike.name,
        5: RowItem.price_opt.name,
        6: RowItem.rest_count.name,
    },
    stop_words=[],
    file_templates=["price*.xls", "price*.xlsx"],
    sheet_indexes=[],
    row_item_adaptor=RowItem,
)

autosnab_config = make_parse_config(autosnab_params)


class Autosnab54Parser(BaseParser):
    """
    logic for autosnab54_ru vendor
    """

    def after_row_mapped(self, row_item: RowItem) -> None:
        fill_from_title(row_item)

    @classmethod
    def get_min_rest_count(cls) -> int:
        """min rest count value for skip action"""
        return 0
