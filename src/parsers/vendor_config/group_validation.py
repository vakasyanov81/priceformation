"""Проверка заданных настроек до наследования, без требования полноты секции."""

from domain.exceptions import ConfigValidationError
from domain.product_groups import ProductGroup
from parsers.data_provider.json_fields import RawConfig, read_object
from parsers.vendor_config.columns import read_columns
from parsers.vendor_config.fields import read_int, read_str_list
from parsers.vendor_config.slot_configs import BehaviorConfig, CategoryConfig, PricingConfig, TitleConfig
from parsers.vendor_config.strategy_names import validate_strategy_names

MODEL_KEYS = ('columns', 'category', 'title', 'pricing', 'behavior')


def validate_reading_settings(payload: RawConfig, where: str) -> None:
    """Отсутствие значения допустимо, неверный заданный тип — нет."""
    read_int(payload, 'start_row', where, 1)
    read_str_list(payload, 'file_templates', where, ())


def validate_group_settings(payload: RawConfig, where: str, group: ProductGroup, *, reads_json: bool) -> None:
    """Проверить исходный уровень, даже если следующий уровень его полностью заменит."""
    validate_reading_settings(payload, where)
    if group is ProductGroup.BATTERIES:
        for key in MODEL_KEYS:
            if key in payload:
                raise ConfigValidationError(f'{where} → {key}: поля и стратегии batteries ещё не определены')
        return
    validate_strategy_names(payload, where)
    read_columns(payload, where, reads_json=reads_json)
    CategoryConfig.from_dict(read_object(payload, 'category', where), f'{where} → category')
    TitleConfig.from_dict(read_object(payload, 'title', where), f'{where} → title')
    PricingConfig.from_dict(read_object(payload, 'pricing', where), f'{where} → pricing')
    BehaviorConfig.from_dict(read_object(payload, 'behavior', where), f'{where} → behavior')
