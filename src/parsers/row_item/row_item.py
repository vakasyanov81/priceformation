# -*- coding: utf-8 -*-
"""
price row item description
"""
__author__ = "Kasyanov V.A."

import hashlib

from src.parsers.row_item import row_item_formatter as row_format


class RowItem:
    """
    price row item description
    """

    __CODE__ = "code"
    __CODES__ = "codes"
    __CODE_MAN__ = "code_man"
    __CODE_ART__ = "code_art"
    __HASH_TITLE__ = "hash_title"
    __TITLE__ = "title"
    __TITLE_CHUNKS__ = "title_chunks"

    # purchase price (цена закупочная)
    __PRICE_PURCHASE__ = "price_purchase"
    # recommended price
    __PRICE_RECOMMENDED__ = "price_recommended"
    # цена с учетом наценки
    __PRICE_WITH_MARKUP__ = "price_markup"

    __SUPPLIER_NAME_COLUMN__ = "sup_name"
    __TYPE_PRODUCTION__ = "type_production"
    __BRAND__ = "brand"
    __MANUFACTURER_NAME__ = "manufacturer_name"

    __PERCENT__ = "percent"
    __REST_COUNT__ = "rest_count"
    __RESERVE_COUNT__ = "reserve_count"

    __DELIVERY_PERIOD__ = "delivery_period"
    __CONDITION__ = "condition"

    __AVAILABLE__ = "available"
    __SEASON__ = "season"
    __SPIKE__ = "spike"

    __WIDTH__ = "width"
    __HEIGHT_PERCENT__ = "height_percent"
    __MARK__ = "mark"
    __DIAMETER__ = "diameter"
    __EXT_DIAMETER__ = "ext_diameter"
    __SLOT_COUNT__ = "slot_count"  # кол-во отверстий
    __SLOT_DIAMETER__ = "slot_diameter"  # диаметр отверстий
    __US_AFF_DESIGNATION__ = "american_affiliation_designation"  # американское обозначение принадлежности
    __PCD1__ = "pcd1"
    __PCD2__ = "pcd2"
    __CENTRAL_DIAMETER__ = "central_diameter"
    __TIRE_TYPE__ = "tire_type"
    # Надпись на боковине
    __INSCRIPTION_ON_THE_SIDE__ = "inscription_on_the_side"
    # Тяжелая шина, можно ехать на спущенной
    __RUN_FLAT__ = "run_flat"
    __ET__ = "et"
    __COLOR__ = "color"
    # основной цвет
    __MAIN_COLOR__ = "main_color"
    __PROFILE__ = "profile"
    __INDEX_VELOCITY__ = "index_velocity"
    __INDEX_LOAD__ = "index_load"
    __MODEL__ = "model"
    __CONSTRUCTION_TYPE__ = "construction_type"
    # Ось (ведущая, рулевая...)
    __AXIS__ = "axis"
    # слойность
    __LAYERING__ = "layering"
    # камерность
    __INTIMACY__ = "intimacy"
    # наличие и тип камеры
    __CAMERA_TYPE__ = "camera_type"
    # крепеж
    __FASTENER__ = "fastener"
    __DISK_TYPE__ = "disk_type"
    # вид диска - легковой / грузовой
    __DISK_TYPE_1__ = "disk_type_1"
    # группировка по параметрам, для поиска дублей
    __GROUP_BY_PARAMS__ = "group_by_params"
    # порядок записей в списке
    __ORDER__ = "order"

    def __init__(self, item: dict):
        """init"""
        self._item = item or {}

    @property
    @row_format.code
    def code(self):
        """code"""
        return self._item.get(self.__CODE__)

    @code.setter
    @row_format.code
    def code(self, code):
        """code setter"""
        self._item[self.__CODE__] = code

    @property
    def codes(self) -> list:
        """codes"""
        codes = [self.code, self.code_man, self.code_art]
        codes = [code for code in codes if code]
        return list(set(codes))

    @property
    @row_format.code
    def code_man(self):
        """code manufacturer"""
        return self._item.get(self.__CODE_MAN__)

    @code_man.setter
    @row_format.code
    def code_man(self, code_man):
        """code manufacturer setter"""
        self._item[self.__CODE_MAN__] = code_man

    @property
    @row_format.code
    def code_art(self):
        """article"""
        return self._item.get(self.__CODE_ART__)

    @code_art.setter
    @row_format.code
    def code_art(self, code_art):
        """article setter"""
        self._item[self.__CODE_ART__] = code_art

    @property
    @row_format.text
    def title(self):
        """title"""
        return self._item.get(self.__TITLE__)

    @title.setter
    @row_format.text
    def title(self, title):
        """title setter"""
        self._item[self.__TITLE__] = title

    @property
    @row_format.text
    def manufacturer(self):
        """manufacturer"""
        return self._item.get(self.__MANUFACTURER_NAME__)

    @manufacturer.setter
    @row_format.text
    def manufacturer(self, manufacturer):
        """manufacturer setter"""
        self._item[self.__MANUFACTURER_NAME__] = manufacturer

    @property
    def hash_title(self):
        """hash title"""
        if not self.title:
            return None
        return hashlib.md5(self.title.encode("utf-8")).hexdigest()

    @property
    @row_format.money
    def price_opt(self):
        """price purchase"""
        return self._item.get(self.__PRICE_PURCHASE__)

    @price_opt.setter
    @row_format.money
    def price_opt(self, price_opt):
        """price purchase setter"""
        self._item[self.__PRICE_PURCHASE__] = price_opt

    @property
    @row_format.money
    def price_recommended(self):
        """recommended price"""
        return self._item.get(self.__PRICE_RECOMMENDED__)

    @price_recommended.setter
    @row_format.money
    def price_recommended(self, price_recommended):
        """recommended price setter"""
        self._item[self.__PRICE_RECOMMENDED__] = price_recommended

    @property
    @row_format.money
    def price_markup(self):
        """price with markup"""
        return self._item.get(self.__PRICE_WITH_MARKUP__)

    @price_markup.setter
    @row_format.money
    def price_markup(self, price_markup):
        """price with markup setter"""
        self._item[self.__PRICE_WITH_MARKUP__] = price_markup

    @property
    @row_format.text
    def supplier_name(self):
        """supplier name"""
        return self._item.get(self.__SUPPLIER_NAME_COLUMN__)

    @supplier_name.setter
    @row_format.text
    def supplier_name(self, supplier_name):
        """supplier name setter"""
        self._item[self.__SUPPLIER_NAME_COLUMN__] = supplier_name

    @property
    @row_format.text
    def type_production(self):
        """type production"""
        return self._item.get(self.__TYPE_PRODUCTION__)

    @type_production.setter
    @row_format.text
    def type_production(self, type_production):
        """type production setter"""
        self._item[self.__TYPE_PRODUCTION__] = type_production

    @property
    @row_format.text
    def brand(self):
        """brand"""
        return self._item.get(self.__BRAND__)

    @brand.setter
    @row_format.text
    def brand(self, brand):
        """brand setter"""
        self._item[self.__BRAND__] = brand

    @property
    @row_format.floated
    def percent_markup(self):
        """percent markup"""
        return self._item.get(self.__PERCENT__)

    @percent_markup.setter
    @row_format.floated
    def percent_markup(self, percent_markup):
        """percent markup setter"""
        self._item[self.__PERCENT__] = percent_markup

    @property
    @row_format.integer
    def rest_count(self):
        """rest count"""
        return self._item.get(self.__REST_COUNT__)

    @rest_count.setter
    @row_format.integer
    def rest_count(self, rest_count):
        """rest count setter"""
        self._item[self.__REST_COUNT__] = rest_count

    @property
    @row_format.text
    def season(self):
        """season"""
        return self._item.get(self.__SEASON__)

    @season.setter
    @row_format.text
    def season(self, season):
        """season setter"""
        self._item[self.__SEASON__] = season

    @property
    @row_format.text
    def spike(self):
        """spike"""
        return self._item.get(self.__SPIKE__)

    @spike.setter
    @row_format.text
    def spike(self, spike):
        """spike setter"""
        self._item[self.__SPIKE__] = spike

    @property
    @row_format.integer
    def reserve_count(self):
        """reserve count"""
        return self._item.get(self.__RESERVE_COUNT__)

    @reserve_count.setter
    @row_format.integer
    def reserve_count(self, reserve_count):
        """reserve count"""
        self._item[self.__RESERVE_COUNT__] = reserve_count

    @property
    @row_format.integer
    def delivery_period(self):
        """delivery period"""
        return self._item.get(self.__DELIVERY_PERIOD__)

    @property
    @row_format.text
    def condition(self):
        """condition"""
        return self._item.get(self.__CONDITION__)

    def to_dict(self):
        """to dict"""
        return self._item

    def clone(self):
        """clone"""
        return RowItem(self.to_dict())

    def __repr__(self):
        return str(self.__dict__)

    @property
    @row_format.text
    def width(self):
        """width"""
        return self._item.get(self.__WIDTH__)

    @property
    @row_format.integer
    def height_percent(self):
        """height percent"""
        return self._item.get(self.__HEIGHT_PERCENT__)

    @property
    @row_format.text
    def mark(self):
        """brand"""
        return self._item.get(self.__MARK__)

    @property
    @row_format.text
    def diameter(self):
        """diameter"""
        diameter = self._item.get(self.__DIAMETER__)
        return diameter

    @property
    @row_format.int_or_float
    def ext_diameter(self):
        """external diameter"""
        return self._item.get(self.__EXT_DIAMETER__)

    @property
    @row_format.int_or_float
    def slot_diameter(self):
        """slot diameter"""
        return self._item.get(self.__SLOT_DIAMETER__)

    @property
    @row_format.integer
    def slot_count(self):
        """slot count"""
        return self._item.get(self.__SLOT_COUNT__)

    @property
    @row_format.text
    def us_aff_design(self):
        """american affiliation designation"""
        return self._item.get(self.__US_AFF_DESIGNATION__)

    @property
    @row_format.int_or_float
    def pcd1(self):
        """Диаметр отверстий, предназначенных для болтов крепления колеса (разболтовка)"""
        return self._item.get(self.__PCD1__)

    @property
    @row_format.int_or_float
    def eet(self):
        """Вылет диска"""
        return self._item.get(self.__ET__)

    @property
    @row_format.int_or_float
    def central_diameter(self):
        """disk central diameter"""
        return self._item.get(self.__CENTRAL_DIAMETER__)

    @property
    @row_format.text
    def color(self):
        """color"""
        return self._item.get(self.__COLOR__)

    @property
    @row_format.text
    def tire_type(self):
        """tire type"""
        return self._item.get(self.__TIRE_TYPE__)

    @property
    @row_format.text
    def profile(self):
        """profile"""
        return self._item.get(self.__PROFILE__)

    @property
    @row_format.text
    def index_velocity(self):
        """index velocity"""
        return self._item.get(self.__INDEX_VELOCITY__)

    @property
    @row_format.text
    def index_load(self):
        """index load"""
        return self._item.get(self.__INDEX_LOAD__)

    @property
    @row_format.text
    def model(self):
        """model"""
        return self._item.get(self.__MODEL__)

    @property
    @row_format.text
    def construction_type(self):
        """construction type"""
        return self._item.get(self.__CONSTRUCTION_TYPE__)

    @property
    @row_format.text
    def axis(self):
        """axis"""
        return self._item.get(self.__AXIS__)

    @property
    @row_format.text
    def layering(self):
        """layering"""
        return self._item.get(self.__LAYERING__)

    @property
    @row_format.text
    def camera_type(self):
        """camera_type"""
        return self._item.get(self.__CAMERA_TYPE__)

    @property
    @row_format.text
    def intimacy(self):
        """intimacy"""
        return self._item.get(self.__INTIMACY__)

    @property
    @row_format.integer
    def order(self) -> int:
        """Порядковый номер в списке"""
        return self._item.get(self.__ORDER__)

    @order.setter
    @row_format.integer
    def order(self, order: int):
        """order"""
        self._item[self.__ORDER__] = order

    @property
    @row_format.integer
    def group_by_params(self) -> int:
        """ID группы наименований с одинаковыми параметрами. Поле нужно для целей поиска дублей наименований."""
        return self._item.get(self.__GROUP_BY_PARAMS__)

    @group_by_params.setter
    @row_format.integer
    def group_by_params(self, group_id: int):
        """group_by_params"""
        self._item[self.__GROUP_BY_PARAMS__] = group_id
