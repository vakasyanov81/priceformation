"""Идентификаторы товарных групп, независимые от категорий и размещения результата."""

from enum import StrEnum, unique
from typing import NamedTuple


@unique
class ProductGroup(StrEnum):
    """Известные группы; наличие идентификатора не означает доступность обработчика."""

    TIRE_AND_DISK = 'tire_and_disk'
    BATTERIES = 'batteries'

    @property
    def display_name(self) -> str:
        """Название для пользователя; не используется как ключ конфигурации."""
        return {
            ProductGroup.TIRE_AND_DISK: 'шины + диски',
            ProductGroup.BATTERIES: 'аккумуляторы',
        }[self]


class DuplicateGroupKey(NamedTuple):
    """Внешний адрес группы дублей; локальный номер уникален только внутри товарной группы."""

    product_group: ProductGroup
    local_group_id: int
