"""Идентификаторы товарных групп, независимые от категорий и размещения результата."""

from enum import StrEnum, unique


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
