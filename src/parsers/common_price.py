# -*- coding: utf-8 -*-
"""
Make parse all price and make inner and drom prices
"""
__author__ = "Kasyanov V.A."

import time
from typing import TypeVar

from src.core import warn_msg, err_msg, log_msg
from src.parsers.all_vendors import all_vendor_supplier_info
from src.parsers.base_parser.base_parser import BaseParser, Parser
from src.parsers.base_parser.base_parser_config import ParseConfiguration
from src.parsers.base_parser.nomenclature_correction import get_nomenclature_corrected_title
from src.parsers.data_provider.vendor_list import VendorListConfigFileError
from src.parsers.row_item.row_item import RowItem
from src.parsers.writer.templates.all_templates import all_writer_templates
from src.parsers.writer.xls_writer import XlsWriter
from src.parsers.writer.xwlt_driver import XlsxWriterDriver

SupplierName = str
SupplierCode = str

VendorList = TypeVar("VendorList", bound=list[tuple[type[Parser], type[ParseConfiguration] | None]])


class CommonPrice:
    """
    Make parse all price and make inner and drom prices
    """

    def __init__(self, xls_writer=XlsWriter, write_driver=XlsxWriterDriver):
        """init"""
        self.xls_writer = xls_writer
        self.write_driver = write_driver
        self._result = []

    def parse_all_vendors(self, vendors: VendorList):
        """
        make parse all prices
        :return:
        """
        start_time = time.time()
        log_msg("\n============== Начало разбора прайсов =================\n", need_print_log=True)
        for vendor, vendor_config in vendors:
            _parser = vendor(vendor_config)
            try:
                self._result += _parser.parse()
            except VendorListConfigFileError:
                warn_msg(
                    "Отсутствует файл конфигурации parse_config/vendor_list.json",
                    need_print_log=True,
                )
            except Exception as exc:
                err_msg(f"Ошибка разбора прайса поставщика {repr(_parser)} // {str(exc)}")
                raise exc
        self.group_by_params()
        elapsed_time = time.time() - start_time

        log_msg(
            f"\n===== Окончание разбора прайсов ({elapsed_time:.2f} секунд) ========\n",
            need_print_log=True,
        )

    def group_by_params(self):
        """Группировка списка по параметрам"""
        self.set_order()
        group_id = 0
        current_key = None
        double_items = []
        result = sorted(self.get_result(), key=self.group_key)
        for item in result:
            _key = self.group_key(item)
            if current_key != _key:
                current_key = _key
                group_id += 1
                self.mark_double_items(double_items)
                double_items = []
            else:
                double_items.append(item)
            item.group_by_params = group_id

        self._result = sorted(result, key=lambda x: x.order)

    @classmethod
    def mark_double_items(cls, items: list[RowItem]):
        if len(items) > 1:
            min_price_item = sorted(items, key=lambda x: x.price_markup)[0]
            for item in items:
                if item.order == min_price_item.order:
                    item.double_candidate = True
                else:
                    item.is_double = False

    def set_order(self):
        result = []
        current_order = 1
        for item in self.get_result():
            item.order = current_order
            current_order += 1
            result.append(item)
        self._result = result

    @classmethod
    def group_key(cls, item_: RowItem):
        width = item_.width or ""
        diameter = item_.diameter or ""
        profile = item_.profile or ""
        velocity = item_.index_velocity or ""
        load = item_.index_load or ""
        model = item_.model or ""
        mark = (item_.manufacturer or "").lower().capitalize()

        axis = item_.axis or ""
        layering = item_.layering or ""
        intimacy = item_.intimacy or ""

        slot_count = item_.slot_count or ""
        dia = item_.central_diameter or ""
        slot_diameter = item_.slot_diameter or ""
        color = item_.color or ""
        _et = item_.eet or ""
        brand = item_.brand or ""

        return (
            item_.type_production,
            width,
            diameter,
            profile,
            velocity,
            load,
            model,
            mark,
            axis,
            layering,
            intimacy,
            slot_count,
            dia,
            slot_diameter,
            color,
            brand,
        )

    @classmethod
    def supplier_info(cls) -> dict[SupplierCode, SupplierName]:
        """Supplier info"""
        return all_vendor_supplier_info()

    def get_result(self):
        """get result"""
        return self._result

    def nomenclature_title_correction(self):
        """make correct nomenclature title"""
        for item in self._result:
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
                BaseParser.to_raw_result(self._result),
                write_template,
            )
