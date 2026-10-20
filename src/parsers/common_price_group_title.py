"""Одно название на группу дублей: название эталона плюс признаки шины, которые есть у других позиций группы.

Эталон — позиция с самой полной моделью (``Road Runner PS-1`` полнее ``Road Runner``); среди равных по полноте
побеждает поставщик с меньшим ``title.reference_priority``, дальше — название по алфавиту, чтобы результат
не зависел от порядка прайсов. Название эталона уже собрано каноническим сборщиком, поэтому его не пересобирают:
к хвосту после нагрузки+скорости добавляются ``XL``, камерность, ``M+S``, ``3PMSF`` и ось, найденные хотя бы
у одной позиции группы (у поставщика без этого токена в прайсе название всё равно совпадёт с остальными).
У групп без модели (камеры, ободные ленты) эталон — самое длинное название.
"""

from collections.abc import Callable, Mapping

from domain.row_item.row_item import RowItem
from parsers.common_price_model import model_tokens
from parsers.common_price_title_tail import merge_tails, split_title

_NO_PRIORITY = 1_000_000
_MIN_TITLES_TO_UNIFY = 2

type _SortKey = Callable[[RowItem], tuple[int, int, str]]


def unify_group_title(group: list[RowItem], priority: Mapping[str, int]) -> None:
    """Всем позициям группы дублей назначить одно название."""
    if len({row_item.identity.title for row_item in group}) < _MIN_TITLES_TO_UNIFY:
        return
    ordered = sorted(group, key=_reference_key(group, priority))
    title = _merged_title(ordered[0], ordered[1:])
    for row_item in group:
        row_item.set_field('title', title)


def _reference_key(group: list[RowItem], priority: Mapping[str, int]) -> _SortKey:
    """Ключ выбора эталона: полнее модель (нет моделей — длиннее название), выше очередь, название по алфавиту."""
    has_models = any(_model_size(row_item) for row_item in group)

    def key(row_item: RowItem) -> tuple[int, int, str]:
        title = row_item.identity.title or ''
        fullness = _model_size(row_item) if has_models else len(title.split())
        return -fullness, priority.get(row_item.vendor.supplier_name or '', _NO_PRIORITY), title

    return key


def _model_size(row_item: RowItem) -> int:
    identity = row_item.identity
    return len(model_tokens(identity.model, identity.manufacturer, identity.brand))


def _merged_title(reference: RowItem, others: list[RowItem]) -> str:
    """Название эталона с признаками шины всей группы; без нагрузки+скорости в названии — как есть."""
    split = split_title(reference)
    if split is None:
        return reference.identity.title or ''
    head, tail = split
    other_tails = [other_split[1] for other in others if (other_split := split_title(other))]
    return ' '.join([*head, *merge_tails(tail, other_tails)])
