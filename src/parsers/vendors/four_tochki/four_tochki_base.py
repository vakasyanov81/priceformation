"""
base logic for four_tochki vendor
"""

from parsers.base_parser.base_parser import BaseParser, ParserParams
from parsers.base_parser.base_parser_config import ParseParamsSupplier
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
    def get_current_category(cls, item):
        """getting current category"""
        raise NotImplementedError()

    @classmethod
    def set_category(cls, item) -> None:
        """set category to row price item"""
        item.type_production = cls.get_current_category(item)

    def process(self):
        """parse process"""
        res = super().process()
        for item in self.result:
            self.add_price_markup(item)
            self.skip_by_min_rest(item)
            self.set_category(item)
            # self.correction_category(item)
        return res
