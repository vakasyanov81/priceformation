"""
# stk
"""

from parsers.base_parser.base_parser import MarkupSkipCategoryParser
from parsers.base_parser.base_parser_config import (
    ParseParamsSupplier,
    ParserParams,
    make_parse_config,
)
from parsers.row_item.row_item import RowItem

STK_START_ROW = 14

stk_params = ParserParams(
    supplier=ParseParamsSupplier(folder_name="stk", name="STK", code="7"),
    start_row=STK_START_ROW,
    sheet_info="",
    columns={
        1: RowItem.code.name,
        2: RowItem.title.name,
        3: RowItem.price_opt.name,
        4: RowItem.rest_count.name,
    },
    stop_words=[],
    file_templates=["price*.xls", "price*.xlsx"],
    sheet_indexes=[],
    row_item_adaptor=RowItem,
)

stk_config = make_parse_config(stk_params)


class STKParser(MarkupSkipCategoryParser):
    """
    parser for Greenstone vendor
    """
