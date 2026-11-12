"""Проверка заданных настроек до наследования, без требования полноты секции."""

from domain.exceptions import ConfigValidationError
from domain.product_groups import ProductGroup
from parsers.data_provider.json_fields import RawConfig, read_object
from parsers.vendor_config.battery_settings import validate_battery_settings
from parsers.vendor_config.columns import read_columns
from parsers.vendor_config.fields import read_int, read_str_list
from parsers.vendor_config.row_selector import RowSelector
from parsers.vendor_config.section_selector import SectionSelector
from parsers.vendor_config.slot_configs import BehaviorConfig, CategoryConfig, PricingConfig, TitleConfig
from parsers.vendor_config.strategy_names import validate_strategy_names

MODEL_KEYS = ('columns', 'category', 'title', 'pricing', 'behavior')


def validate_reading_settings(payload: RawConfig, where: str) -> None:
    """Отсутствие значения допустимо, неверный заданный тип — нет."""
    read_int(payload, 'start_row', where, 1)
    read_str_list(payload, 'file_templates', where, ())


def validate_group_settings(
    payload: RawConfig, where: str, group: ProductGroup, *, reads_json: bool, section_level: bool = False
) -> None:
    """Проверить исходный уровень, даже если следующий уровень его полностью заменит."""
    validate_reading_settings(payload, where)
    _validate_row_selector(payload, where, section_level)
    SectionSelector.from_payload(payload, where)
    if group is ProductGroup.BATTERIES:
        validate_battery_settings(payload, where, reads_json=reads_json)
        return
    _validate_tire_settings(payload, where, reads_json=reads_json)


def _validate_tire_settings(payload: RawConfig, where: str, *, reads_json: bool) -> None:
    """Проверить слоты и колонки шинной модели отдельно от соседних групп."""
    validate_strategy_names(payload, where)
    read_columns(payload, where, reads_json=reads_json)
    CategoryConfig.from_dict(read_object(payload, 'category', where), f'{where} → category')
    TitleConfig.from_dict(read_object(payload, 'title', where), f'{where} → title')
    PricingConfig.from_dict(read_object(payload, 'pricing', where), f'{where} → pricing')
    BehaviorConfig.from_dict(read_object(payload, 'behavior', where), f'{where} → behavior')


def _validate_row_selector(payload: RawConfig, where: str, section_level: bool) -> None:
    if 'row_selector' not in payload:
        return
    if not section_level:
        raise ConfigValidationError(f'{where} → row_selector: селектор задаётся только в секции и не наследуется')
    RowSelector.from_dict(payload.get('row_selector'), f'{where} → row_selector')
