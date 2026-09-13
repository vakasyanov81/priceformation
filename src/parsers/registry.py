"""
Vendor registry: decorator-based registration of parsers.

Usage::

    from parsers.registry import register_vendor

    @register_vendor("poshk", markup_policy="map_on_opt")
    class PoshkParser(BaseParser):
        ...
"""

import importlib
from collections.abc import Callable
from typing import Literal

from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.base_parser_config import (
    ParseConfiguration,
    ParserParams,
    make_parse_config,
)
from parsers.base_parser.markup_policy import (
    IdentityMarkupPolicy,
    MarkupPolicy,
    RecommendedOrMapMarkupPolicy,
    make_map_on_opt_markup_policy,
    make_markup_policy,
)

# Type aliases (re-exported for convenience)
VendorEntry = tuple[type[BaseParser], ParseConfiguration]

MarkupPolicySpec = type[MarkupPolicy] | Literal['map_on_opt', 'identity', 'recommended_or_map'] | None

# List of vendor modules to import if registry is empty
_VENDORS_TO_IMPORT = (
    'parsers.vendors.autosnab54_ru',
    'parsers.vendors.four_tochki.four_tochki_sheet1',
    'parsers.vendors.four_tochki.four_tochki_sheet2',
    'parsers.vendors.mim.mim_1sheet',
    'parsers.vendors.mim.mim_2sheet',
    'parsers.vendors.mim.mim_3sheet',
    'parsers.vendors.pioner',
    'parsers.vendors.poshk',
    'parsers.vendors.stk',
    'parsers.vendors.zapaska_disk_json',
    'parsers.vendors.zapaska_tire_json',
)

# Module-level registry (private)
_registry: dict[str, type[BaseParser]] = {}


def _ensure_vendors_imported() -> None:
    """Импортировать модули вендоров из _VENDORS_TO_IMPORT, чтобы заполнить реестр."""
    if _registry:
        return
    for module_name in _VENDORS_TO_IMPORT:
        importlib.import_module(module_name)


def register_vendor(
    code: str,
    *,
    markup_policy: MarkupPolicySpec = None,
    enabled_by_default: bool = True,
) -> Callable[[type[BaseParser]], type[BaseParser]]:
    """Декоратор: регистрирует класс парсера в глобальном реестре.

    Args:
        code: Уникальный код вендора.
        markup_policy: Политика наценки — строка-ключ, класс MarkupPolicy или None.
        enabled_by_default: Включён ли вендор по умолчанию.
    """

    def wrapper(cls: type[BaseParser]) -> type[BaseParser]:
        cls._vendor_code = code  # type: ignore[attr-defined]
        cls._markup_policy_type = markup_policy  # type: ignore[attr-defined]
        cls._enabled_by_default = enabled_by_default  # type: ignore[attr-defined]
        _registry[code] = cls
        return cls

    return wrapper


config_name_map: dict[str, str] = {
    'autosnab54_ru': 'autosnab_config',
    'four_tochki_sheet1': 'fourtochki_sheet_1_config',
    'four_tochki_sheet2': 'fourtochki_sheet_2_config',
    'mim_1sheet': 'mim_sheet_1_config',
    'mim_2sheet': 'mim_sheet_2_config',
    'mim_3sheet': 'mim_sheet_3_config',
    'zapaska_disk_json': 'zapaska_config',
    'zapaska_tire_json': 'zapaska_tire_config',
}


def _get_config_for_vendor(vendor_cls: type[BaseParser]) -> ParseConfiguration | None:
    """Получить config для вендора: make_config, затем атрибут модуля, затем parser_params."""
    config = _config_from_make_config(vendor_cls)
    if config is not None:
        return config
    config = _module_level_config(vendor_cls)
    if config is not None:
        return config
    return _config_from_parser_params(vendor_cls)


def _config_from_make_config(vendor_cls: type[BaseParser]) -> ParseConfiguration | None:
    """Config из классового make_config; не-ParseConfiguration — fallback на другие источники."""
    config_func = getattr(vendor_cls, 'make_config', None)
    if not callable(config_func):
        return None
    result = config_func()
    if isinstance(result, ParseConfiguration):
        return result
    return None


def _module_level_config(vendor_cls: type[BaseParser]) -> ParseConfiguration | None:
    """Config из атрибута модуля: по маппингу имён или <module_name>_config."""
    module = importlib.import_module(vendor_cls.__module__)
    module_name = vendor_cls.__module__.split('.')[-1]
    config_name = config_name_map.get(module_name, f'{module_name}_config')
    config = getattr(module, config_name, None)
    if isinstance(config, ParseConfiguration):
        return config
    return None


def _config_from_parser_params(vendor_cls: type[BaseParser]) -> ParseConfiguration | None:
    """Собрать config из parser_params, если они есть."""
    params_func = getattr(vendor_cls, 'parser_params', None)
    if not callable(params_func):
        return None
    result = params_func()
    if isinstance(result, ParserParams):
        return make_parse_config(result)
    return None


def all_vendors_from_registry() -> list[VendorEntry]:
    """Собрать список (класс, config) из зарегистрированных вендоров."""
    if not _registry:
        _ensure_vendors_imported()

    vendors: list[VendorEntry] = []
    for vendor_cls in _registry.values():
        config = _get_config_for_vendor(vendor_cls)
        if config is not None:
            vendors.append((vendor_cls, config))
    return vendors


def vendor_markup_policy_for(
    vendor_cls: type[BaseParser],
    vendor_config: ParseConfiguration,
) -> MarkupPolicy | None:
    """Построить политику наценки по атрибуту _markup_policy_type класса."""
    policy_type = getattr(vendor_cls, '_markup_policy_type', None)
    if policy_type is None:
        return None
    if policy_type == 'identity':
        return IdentityMarkupPolicy.create()
    if policy_type == 'map_on_opt':
        return make_map_on_opt_markup_policy(vendor_config)
    if policy_type == 'recommended_or_map':
        return RecommendedOrMapMarkupPolicy.from_config(vendor_config)
    # policy_type is a MarkupPolicy class
    if isinstance(policy_type, type) and issubclass(policy_type, MarkupPolicy):
        # For custom MarkupPolicy subclasses, use make_markup_policy as fallback
        return make_markup_policy(vendor_config)
    return None


def clear_registry() -> None:
    """Очистить реестр (для тестов)."""
    _registry.clear()
