# -*- coding: utf-8 -*-
"""
price row item description for mim vendor
"""
__author__ = "Kasyanov V.A."

from src.parsers.row_item import row_item_formatter as row_format
from src.parsers.row_item.row_item import RowItem


class RowItemMim(RowItem):
    """
    price row item description for mim vendor
    """

    __WIDTH__ = "width"
    __HEIGHT_PERCENT__ = "height_percent"
    __MARK__ = "mark"
    __DIAMETER__ = "diameter"
    __EXT_DIAMETER__ = "ext_diameter"
    __SLOT_COUNT__ = "slot_count"  # кол-во отверстий
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
    @row_format.integer
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
