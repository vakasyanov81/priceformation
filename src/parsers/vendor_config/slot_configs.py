"""Слоты конфигурации поставщика: категория, заголовок, наценка, поведение."""

from dataclasses import dataclass, field
from typing import Any

from parsers.data_provider.json_fields import as_config_object, read_flag, read_number, read_object
from parsers.data_provider.models import MarkupRulesConfig
from parsers.vendor_config.field_map import read_field_map
from parsers.vendor_config.fields import read_int, read_int_list, read_str_list, read_str_map, read_text

DEFAULT_MIN_REST = 4
DEFAULT_CATEGORY_STRATEGY = 'none'
DEFAULT_TITLE_STRATEGY = 'default'
DEFAULT_POLICY = 'base'
REST_COUNT = 'count'
DEFAULT_PIPELINE = ('title', 'min_rest', 'category', 'markup')


@dataclass(frozen=True, slots=True)
class CategoryConfig:
    """Стратегия категории строки (слот `category`).

    `size_fields` дополняет категорию: категория, определённая по размеру
    названия (теми же правилами, что независимый `ProductTypeClassifier`),
    → поля позиции. Независимо от стратегии слота: Пошк/СТК/Пионер получают
    сезон «Всесезонная» у грузовых и спецшин.

    `calculate_type` включает слой независимого типа (`ProductTypeClassifier`):
    заявленный стратегией тип сохраняется для сверки, а в `type_production`
    пишется вычисленный; расхождение помечается `type_corrected`.

    `light_truck_by_diameter` (для `field_map`) — тип «Легковая шина» от поставщика заменяется на
    «Легкогрузовая шина», если в диаметре есть суффикс `C`/`LT` (Форточки: внедорожные `vned` в размере `15C`).
    """

    strategy: str = DEFAULT_CATEGORY_STRATEGY
    fixed_value: str = ''
    field_name: str = ''
    mapping: dict[str, str] = field(default_factory=dict)
    default_value: str = ''
    unknown_skip: bool = False
    zero_rest_categories: tuple[str, ...] = ()
    size_fields: dict[str, dict[str, str]] = field(default_factory=dict)
    calculate_type: bool = False
    light_truck_by_diameter: bool = False

    @classmethod
    def from_dict(cls, raw: Any, where: str) -> CategoryConfig:
        """Разобрать слот `category`: имя стратегии и её параметры."""
        payload = as_config_object(raw, where)
        return cls(
            strategy=read_text(payload, 'strategy', where, DEFAULT_CATEGORY_STRATEGY),
            fixed_value=read_text(payload, 'value', where, ''),
            field_name=read_text(payload, 'field', where, ''),
            mapping=read_str_map(payload, 'map', where),
            default_value=read_text(payload, 'default', where, ''),
            unknown_skip=read_flag(payload, 'unknown_skip', where),
            zero_rest_categories=read_str_list(payload, 'zero_rest_categories', where, ()),
            size_fields=read_field_map(payload, 'size_fields', where),
            calculate_type=read_flag(payload, 'calculate_type', where),
            light_truck_by_diameter=read_flag(payload, 'light_truck_by_diameter', where),
        )


@dataclass(frozen=True, slots=True)
class TitleConfig:
    """Стратегия заголовка строки (слот `title`).

    `markers` дополняет стратегию: подстрока исходного названия → поля позиции.
    Название содержит маркер — незаполненные поля получают заданные значения
    (Пошк: ``шип`` → ``season: зима``, ``spike: да``).
    `params_from_title` включает извлечение параметров из названия в поля позиции
    (шины: размер, нагрузка, скорость, слойность, камерность, модель; диски: размер,
    крепёж, ET, DIA, толщина, цвет, тип); название не меняется.
    `params_first` (с `params_from_title`) разбирает исходное название до сборки: поля позиции
    заполняются из него, и сборка (`tire_compose`, `disk_compose`) строит название по ним.
    `compose` (с `params_from_title`) пересобирает название шины из полей позиции в каноническом порядке
    (`nomenclature_title.TireTitleTokens`); бренд, модель, индексы, слойность, камерность и ось берутся из полей,
    размер — из названия. Название не из шины (камера, диск) не меняется; шина без разбираемого размера
    остаётся нормализованным текстом поставщика и считается в `titles_not_composed`.
    `camera_by_kind` (для `poshk_stk_tire_compose`) — карта «слово вида шины в названии → камерность»:
    если в названии камерности нет, в него добавляется значение первого найденного слова
    (Пошк: ``автошина`` → ``TT``, ``автопокрышка`` → ``TL``).
    `reference_priority` — очередь поставщика среди эталонов названия группы дублей (1 — первый; 0 — не задана,
    поставщик идёт после всех заданных): среди позиций с равно полной моделью название берётся у эталона.
    """

    strategy: str = DEFAULT_TITLE_STRATEGY
    variant: str = ''
    aliases: bool = False
    fallback_brand: str = ''
    params_from_title: bool = False
    params_first: bool = False
    compose: bool = False
    markers: dict[str, dict[str, str]] = field(default_factory=dict)
    camera_by_kind: dict[str, str] = field(default_factory=dict)
    reference_priority: int = 0

    @classmethod
    def from_dict(cls, raw: Any, where: str) -> TitleConfig:
        """Разобрать слот `title`."""
        payload = as_config_object(raw, where)
        return cls(
            strategy=read_text(payload, 'strategy', where, DEFAULT_TITLE_STRATEGY),
            variant=read_text(payload, 'variant', where, ''),
            aliases=read_flag(payload, 'aliases', where),
            fallback_brand=read_text(payload, 'fallback_brand', where, ''),
            params_from_title=read_flag(payload, 'params_from_title', where),
            params_first=read_flag(payload, 'params_first', where),
            compose=read_flag(payload, 'compose', where),
            markers=read_field_map(payload, 'markers', where),
            camera_by_kind=read_str_map(payload, 'camera_by_kind', where),
            reference_priority=read_int(payload, 'reference_priority', where, 0),
        )


@dataclass(frozen=True, slots=True)
class PricingConfig:
    """Наценки поставщика (слот `pricing`).

    `rules` разбирается той же моделью, что и `<supplier>_markup_rules.json`;
    для политики с порогом те же `rules` несут `threshold`/`low`/`high`.
    """

    policy: str = DEFAULT_POLICY
    rules: MarkupRulesConfig = field(default_factory=MarkupRulesConfig)
    threshold: float = 0
    low: float = 0
    high: float = 0

    @classmethod
    def from_dict(cls, raw: Any, where: str) -> PricingConfig:
        """Разобрать слот `pricing`."""
        payload = as_config_object(raw, where)
        rules_payload = read_object(payload, 'rules', where)
        rules_where = f'{where} → rules'
        return cls(
            policy=read_text(payload, 'policy', where, DEFAULT_POLICY),
            rules=MarkupRulesConfig.from_dict(rules_payload, rules_where),
            threshold=read_number(rules_payload, 'threshold', rules_where),
            low=read_number(rules_payload, 'low', rules_where),
            high=read_number(rules_payload, 'high', rules_where),
        )


@dataclass(frozen=True, slots=True)
class BehaviorConfig:
    """Поведение разбора поставщика (секция `behavior`).

    `warehouse_cities` — оставить остатки только на складах этих городов (пусто — без фильтра).
    `order_from_warehouse_name` — «под заказ» и срок доставки берутся из названия склада.
    `api_types` — id категорий, выгружаемых по API поставщика (МИМ); пусто — набор по умолчанию.
    """

    min_rest: int = DEFAULT_MIN_REST
    rest: str = REST_COUNT
    skip_markup_without_opt: bool = False
    zero_rest_without_category: bool = False
    collect_missing_recommended: bool = False
    find_manufacturer_on_enrich: bool = True
    pipeline: tuple[str, ...] = DEFAULT_PIPELINE
    warehouse_cities: tuple[str, ...] = ()
    order_from_warehouse_name: bool = False
    api_types: tuple[int, ...] = ()

    @classmethod
    def from_dict(cls, raw: Any, where: str) -> BehaviorConfig:
        """Разобрать секцию `behavior`."""
        payload = as_config_object(raw, where)
        return cls(
            min_rest=read_int(payload, 'min_rest', where, DEFAULT_MIN_REST),
            rest=read_text(payload, 'rest', where, REST_COUNT),
            skip_markup_without_opt=read_flag(payload, 'skip_markup_without_opt', where),
            zero_rest_without_category=read_flag(payload, 'zero_rest_without_category', where),
            collect_missing_recommended=read_flag(payload, 'collect_missing_recommended', where),
            find_manufacturer_on_enrich=read_flag(payload, 'find_manufacturer_on_enrich', where, True),
            pipeline=read_str_list(payload, 'pipeline', where, DEFAULT_PIPELINE),
            warehouse_cities=read_str_list(payload, 'warehouse_cities', where, ()),
            order_from_warehouse_name=read_flag(payload, 'order_from_warehouse_name', where),
            api_types=read_int_list(payload, 'api_types', where),
        )
