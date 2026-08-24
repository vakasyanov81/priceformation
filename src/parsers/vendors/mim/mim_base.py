"""
base logic for mim vendor
"""

from parsers.base_parser.base_parser import MarkupSkipCategoryParser
from parsers.base_parser.base_parser_config import ParseParamsSupplier, ParserParams
from parsers.row_item.row_item import RowItem

mim_params = ParserParams(
    supplier=ParseParamsSupplier(folder_name="mim", name="Мим", code="4"),
    start_row=2,
    sheet_info="",
    columns={},
    stop_words=[],
    file_templates=["price*.xls", "price*.xlsx"],
    sheet_indexes=[],
    row_item_adaptor=RowItem,
)


class MimParserBase(MarkupSkipCategoryParser):
    """
    base logic for mim vendor
    """

    @classmethod
    def get_current_category(cls) -> str:
        """getting current category"""
        raise NotImplementedError()

    def set_category(self, row_item: RowItem) -> None:
        """set category to row price item"""
        row_item.type_production = self.get_current_category()
