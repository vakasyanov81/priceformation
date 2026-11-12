"""Подготовка аккумуляторного пакета к записи без изменения предложений."""

from dataclasses import dataclass

from domain.battery.result import BatteryResult
from domain.product_group_handler import OutputFields
from parsers.battery.output_fields import OUTPUT_FIELDS, battery_fields
from parsers.writer.templates.group_output import GroupOutput, WriteExclude


def _keep_row(row: OutputFields, filters: WriteExclude) -> bool:
    checks = (row[key] not in excluded for key, excluded in filters.items())
    return all(checks)


@dataclass(frozen=True)
class BatteryOutputSource:
    """Каждое предложение сохраняет собственные цену, остаток и код."""

    package: BatteryResult

    @property
    def fields(self) -> frozenset[str]:
        return OUTPUT_FIELDS

    @property
    def title_fields(self) -> frozenset[str]:
        return frozenset(('title',))

    def prepare(self, _template_id: str, settings: GroupOutput) -> tuple[OutputFields, ...]:
        """Фильтры применяются к аккумуляторным полям, включая разметку дублей."""
        if settings.id != self.package.product_group:
            raise ValueError('Преобразователь batteries получил настройки другой группы')
        if settings.merge_warehouses:
            raise ValueError('batteries: сведение складов недоступно без отдельных складских данных')
        rows = (battery_fields(position) for position in self.package.positions)
        return tuple(row for row in rows if _keep_row(row, settings.filters))
