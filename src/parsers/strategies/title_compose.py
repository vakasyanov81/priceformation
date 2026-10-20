"""Обёртка стратегии `title`: название шины и диска из полей позиции (`title.compose`)."""

from __future__ import annotations

from domain.row_item.row_item import RowItem
from parsers.nomenclature_brand import brand_label, model_label
from parsers.nomenclature_labels import camera_label, run_flat_label, season_marks_label, xl_label
from parsers.nomenclature_title import TireTitleTokens, compose_disk_title, load_velocity
from parsers.strategies._four_tochki_disk_helper import disk_name_suffix, fill_disk_thickness
from parsers.strategies._tire_title_parser import TireTitleParts, parse_tire_title
from parsers.strategies.product_type import ProductTypeClassifier
from parsers.strategies.product_types import DISK, LIGHT_TRUCK, MOTO, PASSENGER, SPECIAL, TRUCK
from parsers.strategies.protocols import ManufacturerProbe, TitleStrategy
from parsers.strategies.tube_title import compose_tube_title_from_text

_TIRE_TYPES = frozenset((PASSENGER, LIGHT_TRUCK, TRUCK, SPECIAL, MOTO))


class TitleFromFields:
    """Собрать название шины или диска в каноническом порядке из полей позиции, а не копировать текст поставщика.

    Название готовит вложенная стратегия, она же (через ``params_from_title``) заполняет поля позиции.
    Бренд, модель, нагрузка/скорость, слойность, камерность и ось берутся из полей, если они заполнены,
    иначе из разбора названия; размер (с суффиксом ``C``/``LT``, дюймовая запись) — из разбора названия.
    ``XL``, ``M+S``, ``3PMSF`` и ``TL`` — свойства шины, а не шум: остаются, если были в названии поставщика
    или в надписи на боковине.

    Диск собирается по шаблону Форточек (``nomenclature_title.compose_disk_title``): размер, крепёж, ``ET``, DIA,
    цвет, бренд, модель — из полей, хвост (толщина, усиление, завод в скобках) — из текста поставщика.
    Камера и ободная лента: ``Камера|Ободная лента <размер> [бренд] [модель]``
    (``tube_title.compose_tube_title_from_text``); название кольца не меняется. Шина без разобранного размера
    и диск без ширины, диаметра, бренда или модели остаются текстом вложенной стратегии, позиция получает
    пометку ``title_not_composed`` для статистики разбора.
    """

    def __init__(
        self,
        inner: TitleStrategy,
        manufacturer_probe: ManufacturerProbe | None = None,
        classifier: ProductTypeClassifier | None = None,
    ) -> None:
        """Обернуть стратегию, готовящую название и поля; ``manufacturer_probe`` ищет производителя в названии."""
        self._inner = inner
        self._manufacturer_probe = manufacturer_probe or _no_manufacturer
        self._classifier = classifier or ProductTypeClassifier()

    def prepare(self, row_item: RowItem) -> str | None:
        """Подготовить название вложенной стратегией и собрать из него и полей шины каноническое."""
        title = self._inner.prepare(row_item)
        parts = parse_tire_title(title)
        if parts is not None:
            return self._compose(row_item, parts, title or '')
        tube_title = compose_tube_title_from_text(row_item, title, self._manufacturer_probe)
        if tube_title is not None:
            return tube_title
        product_type = self._classifier.classify(row_item)
        if product_type == DISK:
            return self._compose_disk(row_item, title or '')
        if product_type in _TIRE_TYPES:
            row_item.set_field('title_not_composed', True)
        return title

    def _compose_disk(self, row_item: RowItem, title: str) -> str:
        """Название диска из полей; без обязательных полей остаётся текст поставщика."""
        if not _has_disk_fields(row_item):
            row_item.set_field('title_not_composed', True)
            return title
        fill_disk_thickness(row_item)
        return compose_disk_title(row_item, disk_name_suffix(title, row_item.identity.model or ''))

    def _compose(self, row_item: RowItem, parts: TireTitleParts, title: str) -> str:
        tire = row_item.tire
        model = model_label(row_item) or parts.model_name
        return TireTitleTokens(
            parts.size_with_alt(),
            self._brand(row_item, parts, title),
            model,
            load_velocity=load_velocity(row_item) or f'{parts.load}{parts.velocity}',
            xl=xl_label(title, tire.inscription_on_the_side),
            layering=tire.layering or parts.layering,
            camera=camera_label(tire.intimacy or parts.intimacy),
            season_marks=season_marks_label(title, tire.inscription_on_the_side),
            axis=tire.axis or parts.axis,
            run_flat='' if run_flat_label(None, model) else run_flat_label(tire.run_flat, title),
        ).compose()

    def _brand(self, row_item: RowItem, parts: TireTitleParts, title: str) -> str:
        """Бренд для названия: производитель, которого найдёт ``ManufacturerFinder`` в тексте поставщика.

        Разбор по алиасам, а не поле: колонка поставщика может нести владельца в скобках
        (``Ikon (Nokian Tyres)``), а после сборки он из названия пропадёт и производитель позиции сменится.
        """
        return self._manufacturer_probe(title) or row_item.identity.manufacturer or parts.brand


def _has_disk_fields(row_item: RowItem) -> bool:
    """Есть всё, без чего название диска не собрать: ширина, диаметр, бренд и модель."""
    size = (row_item.tire.width, row_item.tire.diameter)
    return all(size) and bool(brand_label(row_item) and model_label(row_item))


def _no_manufacturer(_title: str | None) -> str | None:
    """Заглушка поиска производителя: бренд берётся из поля позиции."""


def titles_not_composed_message(count: int) -> str:
    """Сводка по шинам с несобранным названием; пустая строка — таких нет."""
    if not count:
        return ''
    return f'Название шины, диска, камеры или ленты не собрано из полей (оставлен текст поставщика), позиций: {count}'
