"""Результат разбора и группировки прайсов."""

from dataclasses import dataclass, field

from domain.product_group_result import ProductGroupResult, ProductPosition, TireAndDiskResult
from domain.product_groups import ProductGroup
from domain.row_item.row_item import RowItem

type UnknownCategorySkip = tuple[str, str]


@dataclass
class ParseResult:
    """Пакеты выбранных групп и накопленные пропуски; отсутствующая группа не создаётся."""

    groups: dict[ProductGroup, ProductGroupResult[ProductPosition]] = field(default_factory=dict)
    unknown_category_skips: list[UnknownCategorySkip] = field(default_factory=list)
    black_list_skips: int = 0
    type_corrections: int = 0
    title_conflicts: int = 0
    titles_not_composed: int = 0
    homoglyph_fixes: int = 0
    homoglyph_suspects: int = 0

    def add_package(self, package: ProductGroupResult[ProductPosition]) -> None:
        """Добавить выбранную группу или объединить её с позициями следующего поставщика."""
        group = package.product_group
        current = self.groups.get(group)
        if current is None:
            self.groups[group] = package
            return
        self.groups[group] = current.merge(package)

    def replace_package(self, package: ProductGroupResult[ProductPosition]) -> None:
        """Заменить пакет после обработки, не создавая пакеты невыбранных групп."""
        self.groups[package.product_group] = package

    @property
    def tire_and_disk_items(self) -> list[RowItem]:
        """Переходный доступ старых шинных writer и отчётов только к своей группе."""
        package = self.groups.get(ProductGroup.TIRE_AND_DISK)
        if package is None:
            return []
        if not isinstance(package, TireAndDiskResult):
            raise TypeError('Группа tire_and_disk содержит пакет другой модели')
        return list(package.positions)
