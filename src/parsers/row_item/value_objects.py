"""Value objects позиции прайса: семантические группы полей.

Плоский словарь остаётся контрактом сериализации (его видят шаблоны колонок,
jsonl и parse_report), но хранить его на позиции незачем: одинаковые по смыслу
поля лежат рядом и могут проверяться друг о друге.

Типы полей взяты по фактическим входам вендоров и по приведению из реестра
(`field_registry`), а не по прежним аннотациям дескрипторов: `available` несёт
текст, `slot_count` — целое, `pcd1` — целое или дробное.

Все value objects присутствуют всегда; отсутствие данных читается как `None` в
самом поле (`disk.pcd1 is None`), а не как `disk is None`.
"""

from dataclasses import dataclass

_PRICE_DEFAULT = 0


@dataclass(frozen=True, slots=True)
class ProductIdentity:
    """Производитель, бренд, модель и коды позиции."""

    manufacturer: str | None = None
    brand: str | None = None
    model: str | None = None
    title: str | None = None
    code: str | None = None
    code_man: str | None = None
    code_art: str | None = None


@dataclass(frozen=True, slots=True)
class TireDimensions:
    """Характеристики шины: размеры, индексы, конструкция."""

    width: str | None = None
    height_percent: str | None = None
    diameter: str | None = None
    ext_diameter: int | float | None = None
    season: str | None = None
    spike: str | None = None
    index_load: str | None = None
    index_velocity: str | None = None
    tire_type: str | None = None
    run_flat: str | None = None
    inscription_on_the_side: str | None = None
    construction_type: str | None = None
    axis: str | None = None
    layering: str | None = None
    intimacy: str | None = None
    camera_type: str | None = None
    us_aff_designation: str | None = None
    mark: str | None = None


@dataclass(frozen=True, slots=True)
class DiskParameters:
    """Характеристики диска: размеры, крепёж, сверловка, цвет."""

    disk_thickness: str | None = None
    slot_count: int | None = None
    pcd1: int | float | None = None
    pcd2: str | None = None
    eet: int | float | None = None
    central_diameter: int | float | None = None
    fastener: str | None = None
    disk_type: str | None = None
    disk_type_1: str | None = None
    color: str | None = None
    main_color: str | None = None


@dataclass(frozen=True, slots=True)
class Pricing:
    """Цены позиции: закупочная, рекомендуемая, с наценкой."""

    price_opt: float = _PRICE_DEFAULT
    price_recommended: float = _PRICE_DEFAULT
    price_markup: float = _PRICE_DEFAULT
    percent_markup: float | None = None


@dataclass(frozen=True, slots=True)
class Stock:
    """Остатки и сроки поставки."""

    rest_count: int | None = None
    reserve_count: int | None = None
    delivery_period: int | None = None
    available: str | None = None
    condition: str | None = None


@dataclass(frozen=True, slots=True)
class DuplicateInfo:
    """Служебные поля: порядок вывода, группировка, дубли и споры."""

    order: str | None = None
    group_by_params: int | None = None
    is_double: bool | None = None
    double_candidate: bool | None = None
    disputed: str | None = None


@dataclass(frozen=True, slots=True)
class VendorMeta:
    """Поставщик и тип товара."""

    supplier_name: str | None = None
    type_production: str | None = None
