# -*- coding: utf-8 -*-
"""
price row item description
"""
__author__ = "Kasyanov V.A."

import hashlib
from parsers.row_item import row_item_formatter as row_format


class RowItem:
    """
    price row item description
    """
    __CODE__ = 'code'
    __CODES__ = 'codes'
    __CODE_MAN__ = 'code_man'
    __CODE_ART__ = 'code_art'
    __HASH_TITLE__ = 'hash_title'
    __TITLE__ = 'title'
    __TITLE_CHUNKS__ = 'title_chunks'

    # purchase price (цена закупочная)
    __PRICE_PURCHASE__ = 'price_purchase'
    # recommended price
    __PRICE_RECOMMENDED__ = 'price_recommended'
    # цена с учетом наценки
    __PRICE_WITH_MARKUP__ = 'price_markup'

    __SUPPLIER_NAME_COLUMN__ = 'sup_name'
    __TYPE_PRODUCTION__ = 'type_production'
    __BRAND__ = 'brand'
    __MANUFACTURER_NAME__ = 'manufacturer_name'

    __PERCENT__ = 'percent'
    __REST_COUNT__ = 'rest_count'
    __RESERVE_COUNT__ = 'reserve_count'

    __DELIVERY_PERIOD__ = 'delivery_period'
    __CONDITION__ = 'condition'

    __AVAILABLE__ = 'available'

    def __init__(self, item: dict):
        """ init """
        assert isinstance(item, dict)
        self._item = item or {}

    @property
    @row_format.code
    def code(self):
        """ code """
        return self._item.get(
            self.__CODE__
        )

    @code.setter
    @row_format.code
    def code(self, code):
        """ code setter """
        self._item[self.__CODE__] = code

    @property
    def codes(self) -> list:
        """ codes """
        codes = [
            self.code,
            self.code_man,
            self.code_art
        ]
        codes = [
            code for code in codes
            if code
        ]
        return list(set(codes))

    @property
    @row_format.code
    def code_man(self):
        """ code manufacturer """
        return self._item.get(
            self.__CODE_MAN__
        )

    @code_man.setter
    @row_format.code
    def code_man(self, code_man):
        """ code manufacturer setter """
        self._item[self.__CODE_MAN__] = code_man

    @property
    @row_format.code
    def code_art(self):
        """ article """
        return self._item.get(
            self.__CODE_ART__
        )

    @code_art.setter
    @row_format.code
    def code_art(self, code_art):
        """ article setter """
        self._item[self.__CODE_ART__] = code_art

    @property
    @row_format.text
    def title(self):
        """ title """
        return self._item.get(
            self.__TITLE__
        )

    @title.setter
    @row_format.text
    def title(self, title):
        """ title setter """
        self._item[self.__TITLE__] = title

    @property
    @row_format.text
    def manufacturer(self):
        """ manufacturer """
        return self._item.get(
            self.__MANUFACTURER_NAME__
        )

    @manufacturer.setter
    @row_format.text
    def manufacturer(self, manufacturer):
        """ manufacturer setter """
        self._item[self.__MANUFACTURER_NAME__] = manufacturer

    @property
    def hash_title(self):
        """ hash title """
        if not self.title:
            return None
        return hashlib.md5(self.title.encode('utf-8')).hexdigest()

    @property
    @row_format.money
    def price_opt(self):
        """ price purchase """
        return self._item.get(
            self.__PRICE_PURCHASE__
        )

    @price_opt.setter
    @row_format.money
    def price_opt(self, price_opt):
        """ price purchase setter """
        self._item[self.__PRICE_PURCHASE__] = price_opt

    @property
    @row_format.money
    def price_recommended(self):
        """ recommended price """
        return self._item.get(
            self.__PRICE_RECOMMENDED__
        )

    @price_recommended.setter
    @row_format.money
    def price_recommended(self, price_recommended):
        """ recommended price setter """
        self._item[self.__PRICE_RECOMMENDED__] = price_recommended

    @property
    @row_format.money
    def price_markup(self):
        """ price with markup """
        return self._item.get(
            self.__PRICE_WITH_MARKUP__
        )

    @price_markup.setter
    @row_format.money
    def price_markup(self, price_markup):
        """ price with markup setter """
        self._item[self.__PRICE_WITH_MARKUP__] = price_markup

    @property
    @row_format.text
    def supplier_name(self):
        """ supplier name """
        return self._item.get(
            self.__SUPPLIER_NAME_COLUMN__
        )

    @supplier_name.setter
    @row_format.text
    def supplier_name(self, supplier_name):
        """ supplier name setter """
        self._item[self.__SUPPLIER_NAME_COLUMN__] = supplier_name

    @property
    @row_format.text
    def type_production(self):
        """ type production """
        return self._item.get(
            self.__TYPE_PRODUCTION__
        )

    @type_production.setter
    @row_format.text
    def type_production(self, type_production):
        """ type production setter """
        self._item[self.__TYPE_PRODUCTION__] = type_production

    @property
    @row_format.text
    def brand(self):
        """ brand """
        return self._item.get(
            self.__BRAND__
        )

    @brand.setter
    @row_format.text
    def brand(self, brand):
        """ brand setter """
        self._item[self.__BRAND__] = brand

    @property
    @row_format.floated
    def percent_markup(self):
        """ percent markup """
        return self._item.get(
            self.__PERCENT__
        )

    @percent_markup.setter
    @row_format.floated
    def percent_markup(self, percent_markup):
        """ percent markup setter """
        self._item[self.__PERCENT__] = percent_markup

    @property
    @row_format.integer
    def rest_count(self):
        """ rest count """
        return self._item.get(
            self.__REST_COUNT__
        )

    @rest_count.setter
    @row_format.integer
    def rest_count(self, rest_count):
        """ rest count setter """
        self._item[self.__REST_COUNT__] = rest_count

    @property
    @row_format.integer
    def reserve_count(self):
        """ reserve count """
        return self._item.get(
            self.__RESERVE_COUNT__
        )

    @reserve_count.setter
    @row_format.integer
    def reserve_count(self, reserve_count):
        """ reserve count """
        self._item[self.__RESERVE_COUNT__] = reserve_count

    @property
    @row_format.integer
    def delivery_period(self):
        """ delivery period """
        return self._item.get(
            self.__DELIVERY_PERIOD__
        )

    @property
    @row_format.text
    def condition(self):
        """ condition """
        return self._item.get(
            self.__CONDITION__
        )

    def to_dict(self):
        """ to dict """
        return self._item

    def clone(self):
        """ clone """
        return RowItem(self.to_dict())
