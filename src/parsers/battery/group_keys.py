"""Ключи аккумуляторов: неизвестное основное поле запрещает объединение."""

from domain.battery.item import BatteryItem

type BatteryKey = tuple[object, ...]


def normalized(part: object) -> object:
    """Сравнить строки без регистра и лишних пробелов, сохранив числа и bool."""
    if isinstance(part, str):
        return ' '.join(part.split()).casefold() or None
    return part


def identity_key(position: BatteryItem) -> BatteryKey:
    """Коды, название и коммерческие условия не определяют товар."""
    identity, electrical, case = position.identity, position.electrical, position.case
    return tuple(
        map(
            normalized,
            (
                identity.manufacturer_name,
                identity.model,
                electrical.capacity_ah,
                electrical.starting_current_a,
                case.length_mm,
                case.width_mm,
                case.height_mm,
                electrical.terminal_type,
                electrical.polarity,
                electrical.efb,
                electrical.agm,
            ),
        )
    )


def optional_key(position: BatteryItem) -> BatteryKey:
    """Известные дополнительные характеристики обязаны совпадать."""
    case = position.case
    return tuple(
        map(
            normalized,
            (
                case.size_type,
                case.bottom_mount,
                case.serviceable,
                position.electrical.current_standard,
            ),
        )
    )


def resolve_optional(key: BatteryKey, variants: list[set[object]]) -> BatteryKey:
    """Подставить единственный вариант только в сравнительный ключ, не в позицию."""
    compared = zip(key, variants, strict=True)
    return tuple(resolve_part(part, known) for part, known in compared)


def resolve_part(part: object, known: set[object]) -> object:
    """Неизвестное не связывает несколько известных вариантов."""
    if part is None and len(known) == 1:
        return next(iter(known))
    return part


def known_parts(parts: tuple[object, ...]) -> set[object]:
    """Отсутствие характеристики не является её известным вариантом."""
    return set(parts) - {None}
