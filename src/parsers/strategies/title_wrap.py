"""Обёртки стратегии `title` по флагам слота: разбор параметров из названия и сборка шины по полям."""

from __future__ import annotations

from domain.exceptions import ConfigValidationError
from domain.protocols import ConfigProvider
from parsers.base_parser.alias_container import AliasContainer
from parsers.base_parser.base_finder import BaseFinder
from parsers.data_provider.manufacturer_aliases import aliases_for_finder, load_aliases_map
from parsers.strategies.protocols import ManufacturerProbe, TitleStrategy
from parsers.strategies.title_compose import TitleFromFields
from parsers.strategies.title_params import ParamsBeforeTitle, ParamsFromTitle
from parsers.vendor_config.slot_configs import TitleConfig


def check_params_flags(config: TitleConfig, where: str) -> None:
    """`params_first` и `compose` работают только вместе с `params_from_title` и не вместе друг с другом."""
    if config.params_first and not config.params_from_title:
        raise ConfigValidationError(f'{where}: «params_first» работает только вместе с «params_from_title»')
    if config.compose and not config.params_from_title:
        raise ConfigValidationError(f'{where}: «compose» работает только вместе с «params_from_title»')
    if config.compose and config.params_first:
        raise ConfigValidationError(f'{where}: «compose» не сочетается с «params_first»: название собирается один раз')


def wrap_with_params(strategy: TitleStrategy, config: TitleConfig, config_provider: ConfigProvider) -> TitleStrategy:
    """Обернуть разбором параметров из названия (до или после сборки) и, при `compose`, сборкой шины по полям."""
    if config.params_first:
        return ParamsBeforeTitle(strategy)
    if not config.params_from_title:
        return strategy
    parsed = ParamsFromTitle(strategy)
    return TitleFromFields(parsed, manufacturer_probe(config_provider)) if config.compose else parsed


def manufacturer_probe(config_provider: ConfigProvider) -> ManufacturerProbe:
    """Производитель в title по алиасам производителей: тот же поиск, что и у ``ManufacturerFinder``."""
    finder = BaseFinder(AliasContainer(aliases_for_finder(load_aliases_map(config_provider))))
    return lambda title: finder.find_word_in_title(title)[0]
