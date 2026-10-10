"""
Реестр стратегий слота `title`: имя из конфига → фабрика стратегии.
"""

from __future__ import annotations

from collections.abc import Callable

from domain.exceptions import ConfigValidationError
from parsers.base_parser.alias_container import AliasContainer
from parsers.base_parser.base_finder import BaseFinder
from parsers.data_provider.manufacturer_aliases import aliases_for_finder, load_aliases_map
from parsers.data_provider.title_aliases import load_title_aliases
from parsers.strategies.normalize import NormalizeTitle
from parsers.strategies.protocols import BrandProbe, TitleStrategy
from parsers.strategies.stk_title import StkTireCompose
from parsers.strategies.title import (
    DefaultTitle,
    DiskComposeTochki,
    FillFieldsFromTitle,
    ManufacturerFromCategory,
    NormalizeSizeChunks,
    TireCompose,
    TitleWithAliases,
)
from parsers.vendor_config.slot_configs import TitleConfig

_TIRE_VARIANTS = ('mim_simple', 'mim_truck', 'four_tochki')
_DISK_VARIANTS = ('four_tochki',)
_AVAILABLE = (
    'default, normalize_title, normalize_size_chunks, stk_tire_compose, tire_compose, '
    'disk_compose, fill_fields_from_title, manufacturer_from_category'
)
_SIMPLE_STRATEGIES: dict[str, type[TitleStrategy]] = {
    'default': DefaultTitle,
    'normalize_title': NormalizeTitle,
    'normalize_size_chunks': NormalizeSizeChunks,
    'stk_tire_compose': StkTireCompose,
    'fill_fields_from_title': FillFieldsFromTitle,
}

ManufacturerReader = Callable[[], str | None]


def make_title_strategy(
    config: TitleConfig,
    where: str,
    supplier_name: str = '',
    manufacturer_reader: ManufacturerReader | None = None,
) -> TitleStrategy:
    """Собрать стратегию title по слоту конфига; при `aliases` — обернуть картой."""
    strategy = _build_strategy(config, where, manufacturer_reader)
    if config.aliases:
        return TitleWithAliases(strategy, load_title_aliases(supplier_name))
    return strategy


def _build_strategy(
    config: TitleConfig,
    where: str,
    manufacturer_reader: ManufacturerReader | None,
) -> TitleStrategy:
    if config.strategy == 'tire_compose':
        return TireCompose(_require_variant(config.variant, _TIRE_VARIANTS, where))
    if config.strategy == 'disk_compose':
        _require_variant(config.variant, _DISK_VARIANTS, where)
        return DiskComposeTochki()
    if config.strategy == 'manufacturer_from_category':
        return ManufacturerFromCategory(manufacturer_reader or _no_manufacturer)
    if config.strategy == 'normalize_size_chunks':
        probe = _brand_probe() if config.fallback_brand else None
        return NormalizeSizeChunks(config.fallback_brand, probe)
    factory = _SIMPLE_STRATEGIES.get(config.strategy)
    if factory is None:
        raise ConfigValidationError(
            f'{where}: неизвестная стратегия title {config.strategy!r} (доступны: {_AVAILABLE})',
        )
    return factory()


def _require_variant(variant: str, allowed: tuple[str, ...], where: str) -> str:
    if variant not in allowed:
        raise ConfigValidationError(
            f'{where}: неизвестный вариант {variant!r} (ожидается {allowed!r})',
        )
    return variant


def _no_manufacturer() -> str | None:
    """Заглушка: производитель раздела ещё не прочитан."""


def _brand_probe() -> BrandProbe:
    """Детектор бренда в title по алиасам производителей (границы как у BaseFinder)."""
    finder = BaseFinder(AliasContainer(aliases_for_finder(load_aliases_map())))
    return lambda title: finder.find_word_in_title(title)[0] is not None
