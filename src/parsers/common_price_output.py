"""
Make parse all price and make inner and drom prices
"""

from parsers.row_item.row_item import RowItem
from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.nomenclature_correction import get_nomenclature_corrected_title
from parsers.writer.templates.all_templates import all_writer_templates
from parsers.writer.xls_writer import XlsWriter
from parsers.writer.xwlt_driver import XlsxWriterDriver


class CommonPriceOut:
    """
    Make parse all price and make inner and drom prices
    """

    def __init__(self, items: list[RowItem], xls_writer=XlsWriter, write_driver=XlsxWriterDriver):
        """init"""
        self.xls_writer = xls_writer
        self.write_driver = write_driver
        self.items = items

    def nomenclature_title_correction(self):
        """make correct nomenclature title"""
        for item in self.items:
            item.title = get_nomenclature_corrected_title(item.title)

    def write_all_prices(self):
        """
        Make prices for all active templates
        :return:
        """
        # TODO add test
        self.nomenclature_title_correction()
        for write_template in all_writer_templates():
            self.xls_writer(
                self.write_driver(),
                BaseParser.to_raw_result(self.items),
                write_template,
            )
