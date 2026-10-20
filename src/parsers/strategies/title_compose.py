"""Обёртка стратегии `title`: название шины из полей позиции (`title.compose`)."""

from __future__ import annotations

from domain.row_item.row_item import RowItem
from parsers.nomenclature_brand import model_label
from parsers.nomenclature_labels import camera_label, run_flat_label, season_marks_label, xl_label
from parsers.nomenclature_title import TireTitleTokens, load_velocity
from parsers.strategies._tire_title_parser import TireTitleParts, parse_tire_title
from parsers.strategies.product_type import ProductTypeClassifier
from parsers.strategies.product_types import LIGHT_TRUCK, MOTO, PASSENGER, SPECIAL, TRUCK
from parsers.strategies.protocols import ManufacturerProbe, TitleStrategy

_TIRE_TYPES = frozenset((PASSENGER, LIGHT_TRUCK, TRUCK, SPECIAL, MOTO))


class TireTitleFromFields:
    """Собрать название шины в каноническом порядке из полей позиции, а не копировать текст поставщика.

    Название готовит вложенная стратегия, она же (через ``params_from_title``) заполняет поля позиции.
    Бренд, модель, нагрузка/скорость, слойность, камерность и ось берутся из полей, если они заполнены,
    иначе из разбора названия; размер (с суффиксом ``C``/``LT``, дюймовая запись) — из разбора названия.
    ``XL``, ``M+S``, ``3PMSF`` и ``TL`` — свойства шины, а не шум: остаются, если были в названии поставщика
    или в надписи на боковине.

    Название не из шины (камера, диск) не меняется. Шина, у которой размер не разобран, остаётся
    текстом вложенной стратегии, позиция получает пометку ``title_not_composed`` для статистики разбора.
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
        if parts is None:
            if self._is_tire(row_item):
                row_item.set_field('title_not_composed', True)
            return title
        return self._compose(row_item, parts, title or '')

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

    def _is_tire(self, row_item: RowItem) -> bool:
        """Независимый классификатор считает позицию шиной (камера, лента, кольцо, диск — нет)."""
        return self._classifier.classify(row_item) in _TIRE_TYPES


def _no_manufacturer(_title: str | None) -> str | None:
    """Заглушка поиска производителя: бренд берётся из поля позиции."""


def titles_not_composed_message(count: int) -> str:
    """Сводка по шинам с несобранным названием; пустая строка — таких нет."""
    if not count:
        return ''
    return f'Название шины не собрано из полей (оставлен текст поставщика), позиций: {count}'
