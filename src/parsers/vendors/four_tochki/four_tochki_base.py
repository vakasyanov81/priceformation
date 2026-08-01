"""
base logic for four_tochki vendor
"""

from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.base_parser_config import ParseParamsSupplier, ParserParams
from parsers.row_item.row_item import RowItem

fourtochki_params = ParserParams(
    supplier=ParseParamsSupplier(folder_name="four_tochki", name="Форточки", code="5"),
    start_row=2,
    sheet_info="",
    columns={},
    stop_words=[],
    file_templates=["price*.xls", "price*.xlsx"],
    sheet_indexes=[],
    row_item_adaptor=RowItem,
)


class FourTochkiParserBase(BaseParser):
    """
    base logic for four_tochki vendor
    """

    @classmethod
    def get_current_category(cls, row_item: RowItem) -> str:
        """getting current category"""
        raise NotImplementedError()

    @classmethod
    def set_category(cls, row_item: RowItem) -> None:
        """set category to row price item"""
        row_item.type_production = cls.get_current_category(row_item)

    def process(self) -> int:
        """parse process"""
        res = super().process()
        for row_item in self.parsed_items:
            self.add_price_markup(row_item)
            self.skip_by_min_rest(row_item)
            self.set_category(row_item)
            # self.correction_category(item)
        return res
