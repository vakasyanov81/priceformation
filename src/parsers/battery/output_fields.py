"""Преобразование аккумуляторной модели в скалярные поля записи."""

from decimal import Decimal

from domain.battery.field_registry import FIELD_KEYS, BatteryValue
from domain.battery.item import BatteryItem
from domain.battery.offer import BatteryOffer
from domain.product_group_handler import OutputFields, OutputValue

OUTPUT_FIELDS = frozenset((*FIELD_KEYS, 'sale_price', 'group_id', 'is_main', 'absolute_markup', 'percent_markup'))
_COMPACT_NUMBER_FIELDS = frozenset(
    (
        'price_opt',
        'price_recommended',
        'price_markup',
        'sale_price',
        'absolute_markup',
        'percent_markup',
        'length_mm',
        'width_mm',
        'height_mm',
        'weight',
        'capacity_ah',
        'starting_current_a',
    ),
)


def output_value(cell: BatteryValue, field_name: str) -> OutputValue:
    """Decimal передаётся строкой без потери точности в XLSX и JSONL."""
    if isinstance(cell, Decimal):
        if field_name in _COMPACT_NUMBER_FIELDS and cell == cell.to_integral_value():
            return str(int(cell))
        return str(cell)
    return cell


def _markup_values(offer: BatteryOffer) -> tuple[Decimal | None, Decimal | None]:
    """Наценка от итоговой продажи; неизвестные цены не подменяются нулями."""
    purchase = offer.price_opt
    sale = offer.sale_price
    if purchase is None or sale is None:
        return None, None
    margin = sale - purchase
    percent = round(margin / purchase * 100, 2) if purchase else None
    return round(margin, 2), percent


def battery_fields(position: BatteryItem) -> OutputFields:
    """Плоские поля появляются только на границе записи."""
    absolute, percent = _markup_values(position.offer)
    fields: dict[str, BatteryValue] = {
        'title': position.identity.title,
        'manufacturer_name': position.identity.manufacturer_name,
        'model': position.identity.model,
        'code': position.identity.code,
        'code_art': position.identity.code_art,
        'code_man': position.identity.code_man,
        'capacity_ah': position.electrical.capacity_ah,
        'starting_current_a': position.electrical.starting_current_a,
        'current_standard': position.electrical.current_standard,
        'terminal_type': position.electrical.terminal_type,
        'polarity': position.electrical.polarity,
        'efb': position.electrical.efb,
        'agm': position.electrical.agm,
        'length_mm': position.case.length_mm,
        'width_mm': position.case.width_mm,
        'height_mm': position.case.height_mm,
        'size_type': position.case.size_type,
        'bottom_mount': position.case.bottom_mount,
        'serviceable': position.case.serviceable,
        'weight': position.case.weight,
        'price_opt': position.offer.price_opt,
        'price_recommended': position.offer.price_recommended,
        'price_markup': position.offer.price_markup,
        'rest_count': position.offer.rest_count,
        'warranty_months': position.offer.warranty_months,
        'supplier_name': position.offer.supplier_name,
        'price_group': position.offer.price_group,
        'certificate_url': position.offer.certificate_url,
        'group_id': position.duplicate.group_id,
        'is_main': position.duplicate.is_main,
        'sale_price': position.offer.sale_price,
        'absolute_markup': absolute,
        'percent_markup': percent,
    }
    return {key: output_value(cell, key) for key, cell in fields.items()}
