"""Интерфейс обработки группы: доменная модель сохраняется до подготовки вывода."""

from collections.abc import Mapping, Sequence
from typing import Protocol

from domain.product_group_result import ProductGroupResult, ProductPosition
from domain.product_groups import ProductGroup

type InputFields = Mapping[str, object]
type OutputValue = str | int | float | bool | None
type OutputFields = Mapping[str, OutputValue]


class ProductGroupHandler[TPosition: ProductPosition](Protocol):
    """Обработка одной группы с настройками, переданными при сборке реализации.

    Чтение файлов, выбор секций и отображение входных колонок предшествуют
    созданию позиции. Словарь входа не заменяет доменную модель: обработка
    и группировка получают только позиции своей модели и возвращают её пакет.

    Порядок вызовов: create_position → process → group → prepare_output.
    Process включает обогащение, фильтры и завершающие шаги разбора; group
    вызывается после сбора позиций поставщиков одной группы. Обе операции
    могут изменять позиции, исключать их и менять порядок, но не модель
    или группу. Пустой результат сохраняет группу обработчика.

    Prepare_output применяет настройки вывода внутри группы (включая склады
    и дубли) и только затем преобразует позиции в плоские выходные поля.
    Выбор файлов, листов и запись остаются за вызывающим кодом. Ошибки
    валидации и обработки передаются вызывающему коду, а не скрываются.
    """

    @property
    def product_group(self) -> ProductGroup: ...

    def create_position(self, fields: InputFields) -> TPosition:
        """Создать позицию своей модели из уже отображённых входных колонок."""
        ...

    def process(self, positions: Sequence[TPosition]) -> ProductGroupResult[TPosition]:
        """Обработать позиции одной секции и вернуть однородный пакет."""
        ...

    def group(self, package: ProductGroupResult[TPosition]) -> ProductGroupResult[TPosition]:
        """Сгруппировать позиции поставщиков по правилам своей модели."""
        ...

    def prepare_output(self, package: ProductGroupResult[TPosition]) -> tuple[OutputFields, ...]:
        """Подготовить выходные поля, сохраняя правила группы внутри реализации."""
        ...
