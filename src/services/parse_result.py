"""Результат разбора и группировки прайсов."""

from dataclasses import dataclass, field

from domain.product_group_result import ProductGroupResult, ProductPosition, TireAndDiskResult
from domain.product_groups import ProductGroup
from domain.row_item.row_item import RowItem
from services.parse_statistics import GroupStatistics, TireAndDiskDiagnostics


@dataclass
class ParseSelection:
    """Определённый выбор сохраняется и при отказе до получения результата."""

    groups: tuple[ProductGroup, ...] = ()


@dataclass
class ParseResult:
    """Пакеты выбранных групп и накопленные пропуски; отсутствующая группа не создаётся."""

    groups: dict[ProductGroup, ProductGroupResult[ProductPosition]] = field(default_factory=dict)
    statistics: dict[ProductGroup, GroupStatistics] = field(default_factory=dict)
    tire_and_disk_diagnostics: TireAndDiskDiagnostics = field(default_factory=TireAndDiskDiagnostics)
    unrouted_rows: int = 0

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

    def total_statistics(self) -> GroupStatistics:
        """Суммировать только общие счётчики выбранных пакетов."""
        total = GroupStatistics()
        for group, package in self.groups.items():
            counters = self.statistics.get(group, GroupStatistics())
            total.item_count += len(package.positions)
            total.priced_items += counters.priced_items
            total.doubles += counters.doubles
            total.black_list_skips += counters.black_list_skips
        return total

    @property
    def tire_and_disk_items(self) -> list[RowItem]:
        """Переходный доступ старых шинных writer и отчётов только к своей группе."""
        package = self.groups.get(ProductGroup.TIRE_AND_DISK)
        if package is None:
            return []
        if not isinstance(package, TireAndDiskResult):
            raise TypeError('Группа tire_and_disk содержит пакет другой модели')
        return list(package.positions)
