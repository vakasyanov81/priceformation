"""Имена стратегий шин и дисков без сборки обработчиков и IO."""

from domain.exceptions import ConfigValidationError
from parsers.data_provider.json_fields import RawConfig, read_object
from parsers.vendor_config.fields import read_str_list, read_text

CATEGORY_STRATEGIES = (
    'none',
    'fixed',
    'title_keywords',
    'field_map',
    'column_canonical',
    'header_rows',
    'tire_size_category',
)
TITLE_STRATEGIES = (
    'default',
    'normalize_title',
    'normalize_size_chunks',
    'poshk_stk_tire_compose',
    'tire_compose',
    'disk_compose',
    'fill_fields_from_title',
    'manufacturer_from_category',
)
PRICING_POLICIES = ('base', 'identity', 'map_on_opt', 'recommended_or_map', 'recommended_range', 'percent_by_threshold')
REST_STRATEGIES = ('count', 'minus_reserve')
PIPELINE_STEPS = ('title', 'min_rest', 'category', 'markup')


def validate_strategy_names(payload: RawConfig, where: str) -> None:
    """Проверить явно заданные имена до наследования неполных слотов."""
    for slot, key, allowed in (
        ('category', 'strategy', CATEGORY_STRATEGIES),
        ('title', 'strategy', TITLE_STRATEGIES),
        ('pricing', 'policy', PRICING_POLICIES),
        ('behavior', 'rest', REST_STRATEGIES),
    ):
        settings = read_object(payload, slot, where)
        if key in settings:
            _require_name(read_text(settings, key, where), allowed, f'{where} → {slot} → {key}')
    _validate_pipeline(read_object(payload, 'behavior', where), where)


def _validate_pipeline(behavior: RawConfig, where: str) -> None:
    """Проверить каждый шаг по исходному индексу списка."""
    for index, step in enumerate(read_str_list(behavior, 'pipeline', where, ())):
        _require_name(step, PIPELINE_STEPS, f'{where} → behavior → pipeline[{index}]')


def _require_name(name: str, allowed: tuple[str, ...], where: str) -> None:
    """Отклонить чужое имя в исходном месте задания."""
    if name not in allowed:
        available = ', '.join(allowed)
        raise ConfigValidationError(f'{where}: неизвестная стратегия tire_and_disk {name!r} (доступны: {available})')
