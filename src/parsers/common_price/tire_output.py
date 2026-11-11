"""Подготовка пакета шин и дисков к записи по настройкам группы."""

from dataclasses import dataclass, field

from domain.product_group_handler import OutputFields
from domain.product_group_result import TireAndDiskResult
from domain.row_item.field_registry import FIELD_KEYS
from domain.row_item.row_item import RowItem
from parsers.common_price.doubles_order import priority_first
from parsers.common_price.exclude_doubles import exclude_doubles
from parsers.common_price.warehouses import merge_warehouse_rows
from parsers.data_provider.doubles_settings import DoublesSettings
from parsers.writer.templates.group_output import GroupOutput, WriteExclude


def _keep_position(row: RowItem, filters: WriteExclude) -> bool:
    rules = filters.items()
    checks = (row.get_field(key) not in excluded for key, excluded in rules)
    return all(checks)


@dataclass(frozen=True)
class TireOutputSource:
    """Настройки вывода действуют только на связанный пакет шин и дисков."""

    package: TireAndDiskResult
    doubles: DoublesSettings = field(default_factory=DoublesSettings)

    @property
    def fields(self) -> frozenset[str]:
        return frozenset(FIELD_KEYS)

    @property
    def title_fields(self) -> frozenset[str]:
        return frozenset(('title',))

    def prepare(self, template_id: str, settings: GroupOutput) -> tuple[OutputFields, ...]:
        return tuple(row.to_dict() for row in self.positions_for(template_id, settings))

    def positions_for(self, template_id: str, settings: GroupOutput) -> list[RowItem]:
        """Применить правила вывода к модели до передачи её сериализатору."""
        if settings.id != self.package.product_group:
            raise ValueError('Преобразователь tire_and_disk получил настройки другой группы')
        rows = list(self.package.positions)
        if settings.merge_warehouses:
            rows = merge_warehouse_rows(rows)
        if self.doubles.excludes_in(template_id):
            rows = exclude_doubles(rows, self.doubles.priority_suppliers)
        return [row for row in rows if _keep_position(row, settings.filters)]


def double_positions(rows: list[RowItem], settings: DoublesSettings) -> list[RowItem]:
    """Отобрать и упорядочить кандидатов отчёта дублей внутри шинной группы."""
    doubles = [row for row in rows if row.duplicate.is_double or row.duplicate.double_candidate]
    return priority_first(doubles, settings.priority_suppliers)
