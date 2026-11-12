"""Собственные слоты обработки аккумуляторов без шинных настроек."""

from dataclasses import dataclass

from domain.exceptions import ConfigValidationError
from domain.product_groups import ProductGroup
from parsers.data_provider.json_fields import RawConfig, read_object
from parsers.vendor_config.columns import read_columns
from parsers.vendor_config.fields import read_int, read_str_list, read_text

PLANT_LINES = ('XTREME +EFB', 'XTREME Arctic')


@dataclass(frozen=True, slots=True)
class BatterySettings:
    """Линейки задаются явно; цена продажи всегда РРЦ, остаток — минимум одна штука."""

    lines: tuple[str, ...] = PLANT_LINES
    min_rest: int = 1

    @classmethod
    def from_dict(cls, payload: RawConfig, where: str) -> BatterySettings:
        """Проверить каждый заданный слот до наследования и сохранить типизированные настройки."""
        title = _slot(payload, 'title', ('strategy', 'lines'), where)
        pricing = _slot(payload, 'pricing', ('policy',), where)
        behavior = _slot(payload, 'behavior', ('min_rest', 'rest'), where)
        _require_choice(title, 'strategy', 'plant', f'{where} → title')
        _require_choice(pricing, 'policy', 'recommended', f'{where} → pricing')
        _require_choice(behavior, 'rest', 'count', f'{where} → behavior')
        return cls(_read_lines(title, f'{where} → title'), _minimum_rest(behavior, f'{where} → behavior'))


def validate_battery_settings(payload: RawConfig, where: str, *, reads_json: bool) -> None:
    """Колонки проверяются по аккумуляторному реестру; шинного слота category здесь нет."""
    if 'category' in payload:
        raise ConfigValidationError(f'{where} → category: слот недоступен для batteries')
    read_columns(payload, where, reads_json=reads_json, group=ProductGroup.BATTERIES)
    BatterySettings.from_dict(payload, where)


def _slot(payload: RawConfig, key: str, allowed: tuple[str, ...], where: str) -> RawConfig:
    parsed = read_object(payload, key, where)
    for setting in parsed:
        if setting not in allowed:
            raise ConfigValidationError(f'{where} → {key} → {setting}: настройка недоступна для batteries')
    return parsed


def _require_choice(payload: RawConfig, key: str, expected: str, where: str) -> None:
    if read_text(payload, key, where, expected) != expected:
        raise ConfigValidationError(f'{where} → {key}: для batteries поддерживается только {expected}')


def _read_lines(payload: RawConfig, where: str) -> tuple[str, ...]:
    configured = read_str_list(payload, 'lines', where, PLANT_LINES)
    lines = tuple(' '.join(line.split()) for line in configured)
    normalized = {line.casefold() for line in lines}
    if not lines or '' in normalized or len(normalized) != len(lines):
        raise ConfigValidationError(f'{where} → lines: требуется непустой список уникальных непустых линеек')
    return lines


def _minimum_rest(payload: RawConfig, where: str) -> int:
    minimum = read_int(payload, 'min_rest', where, 1)
    if minimum < 1:
        raise ConfigValidationError(f'{where} → min_rest: минимальный остаток должен быть не меньше 1')
    return minimum
