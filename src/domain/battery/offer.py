"""Коммерческие данные предложения аккумулятора."""

from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal

from domain.battery.conversions import integer, number, stock, text
from domain.battery.field_registry import read_field
from domain.battery.values import check_integer, check_number


@dataclass(frozen=True, slots=True)
class BatteryOffer:
    """Закупочная и РРЦ раздельны; остаток уже очищен от резерва поставщиком."""

    price_opt: Decimal | None = None
    price_recommended: Decimal | None = None
    rest_count: int | None = None
    warranty_months: int | None = None
    supplier_name: str | None = None
    price_group: str | None = None
    certificate_url: str | None = None
    price_markup: Decimal | None = None

    def __post_init__(self) -> None:
        check_number(self.price_opt, 'price_opt', positive=False)
        check_number(self.price_recommended, 'price_recommended', positive=False)
        check_number(self.price_markup, 'price_markup', positive=False)
        check_integer(self.rest_count, 'rest_count')
        check_integer(self.warranty_months, 'warranty_months')

    @property
    def sale_price(self) -> Decimal | None:
        """Рассчитанная цена продажи; до обработки используется исходная РРЦ."""
        if self.price_markup is not None:
            return self.price_markup
        return self.price_recommended

    @classmethod
    def from_fields(cls, fields: Mapping[str, object]) -> BatteryOffer:
        """Сохранить точность денежных значений и неизвестные данные."""
        return cls(
            price_opt=read_field(fields, 'price_opt', number),
            price_recommended=read_field(fields, 'price_recommended', number),
            rest_count=read_field(fields, 'rest_count', stock),
            warranty_months=read_field(fields, 'warranty_months', integer),
            supplier_name=read_field(fields, 'supplier_name', text),
            price_group=read_field(fields, 'price_group', text),
            certificate_url=read_field(fields, 'certificate_url', text),
            price_markup=read_field(fields, 'price_markup', number),
        )
