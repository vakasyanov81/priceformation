"""Обработчик аккумуляторов с отдельными стратегиями и типизированным результатом."""

from collections.abc import Sequence
from typing import Literal

from domain.battery.conversions import text
from domain.battery.item import BatteryItem
from domain.battery.result import BatteryResult
from domain.product_group_handler import InputFields, OutputFields
from domain.product_group_result import ProductGroupResult
from domain.product_groups import ProductGroup
from parsers.battery.grouping import group_batteries
from parsers.battery.output_fields import battery_fields
from parsers.battery.plant_fields import normalize_fields
from parsers.battery.processing import log_skipped, publication_issue
from parsers.battery.title import normalize_title
from parsers.vendor_config.battery_settings import BatterySettings


class BatteryHandler:
    """Создание, обработка, группировка и выходные поля аккумуляторов."""

    def __init__(self, settings: BatterySettings, supplier: str) -> None:
        self._settings = settings
        self._supplier = supplier

    @property
    def product_group(self) -> Literal[ProductGroup.BATTERIES]:
        return ProductGroup.BATTERIES

    def create_position(self, fields: InputFields) -> BatteryItem:
        try:
            return BatteryItem.from_fields({**normalize_fields(fields), 'supplier_name': self._supplier})
        except ValueError as exc:
            offer_code = fields.get('code')
            raise ValueError(f'[batteries] {self._supplier}, код {offer_code}: {exc}') from exc

    def process_fields(self, rows: Sequence[InputFields]) -> BatteryResult:
        """Строки разделов без кода отсекаются до преобразования характеристик в доменную модель."""
        product_rows = [fields for fields in rows if text(fields.get('code')) is not None]
        positions = [self.create_position(fields) for fields in product_rows]
        return self.process(positions)

    def process(self, positions: Sequence[BatteryItem]) -> BatteryResult:
        """Проверить публикацию до разбора линейки, чтобы пропуски получили собственную диагностику."""
        kept: list[BatteryItem] = []
        for position in positions:
            issue = publication_issue(position, self._settings.min_rest)
            if issue is not None:
                log_skipped(position, self._supplier, issue)
                continue
            try:
                kept.append(normalize_title(position, self._settings.lines))
            except ValueError as exc:
                offer_code = position.identity.code
                raise ValueError(f'[batteries] {self._supplier}, код {offer_code}: {exc}') from exc
        return BatteryResult(tuple(kept))

    def group(self, package: ProductGroupResult[BatteryItem]) -> BatteryResult:
        """Сгруппировать только аккумуляторы, сохраняя отдельные предложения."""
        return group_batteries(BatteryResult(package.positions))

    def prepare_output(self, package: ProductGroupResult[BatteryItem]) -> tuple[OutputFields, ...]:
        """Проверить модель пакета и сохранить цены и остатки каждого предложения."""
        return tuple(battery_fields(position) for position in BatteryResult(package.positions).positions)
