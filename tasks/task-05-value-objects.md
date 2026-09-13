# Task-05: Value Objects для RowItem

## Проблема

`RowItem` — это God Object с ~40 полями, описывающими разнородные сущности:

- Характеристики шин (`width`, `height_percent`, `diameter`, `season`, `spike`, ...)
- Характеристики дисков (`slot_count`, `pcd1`, `pcd2`, `eet`, `disk_thickness`, ...)
- Цены и наценки (`price_opt`, `price_recommended`, `price_markup`, `percent_markup`)
- Служебные поля (`order`, `group_by_params`, `is_double`, `double_candidate`, `disputed`)
- Производитель/бренд/модель (`manufacturer`, `brand`, `model`, ...)

Проблемы:
- Нет группировки семантически связанных полей.
- Невозможно ввести инварианты (e.g., `diameter` > 0).
- При добавлении нового типа товара (например, масла, АКБ) поля шин/дисков остаются мусором.
- `FieldDescriptor` с `_key_value_store` — это имитация Dict, не дающая типобезопасности.

## Решение

### 1. Ввести Value Objects через dataclasses

```python
@dataclass(frozen=True)
class TireDimensions:
    width: str = ''
    height_percent: str = ''
    diameter: str = ''
    ext_diameter: int | float = 0


@dataclass(frozen=True)
class DiskParameters:
    slot_count: int = 0
    pcd1: int | float = 0
    pcd2: int = 0
    eet: int | float = 0
    central_diameter: int | float = 0
    disk_thickness: str = ''


@dataclass
class Pricing:
    price_opt: float = 0
    price_recommended: float = 0
    price_markup: float = 0
    percent_markup: float = 0


@dataclass
class ProductIdentity:
    manufacturer: str = ''
    brand: str = ''
    model: str = ''
    codes: list[str] = field(default_factory=list)


@dataclass
class DuplicateInfo:
    order: int = 0
    group_by_params: int = 0
    is_double: bool = False
    double_candidate: bool = False
    disputed: str = ''
```

### 2. Новый `RowItem` — композиция

```python
@dataclass
class RowItem:
    title: str = ''
    product_identity: ProductIdentity = field(default_factory=ProductIdentity)
    tire: TireDimensions | None = None
    disk: DiskParameters | None = None
    pricing: Pricing = field(default_factory=Pricing)
    duplicate: DuplicateInfo = field(default_factory=DuplicateInfo)
    # Общие поля:
    supplier_name: str = ''
    type_production: str = ''
    rest_count: int = 0
    ...
```

### 3. Сериализация через плагины

```python
def to_dict(row: RowItem) -> dict[str, Any]:
    result = {
        "title": row.title,
        "code": row.product_identity.codes[0] if row.product_identity.codes else "",
        ...
    }
    if row.tire:
        result.update({
            "width": row.tire.width,
            "height_percent": row.tire.height_percent,
            "diameter": row.tire.diameter,
        })
    return result
```

### 4. Форматеры привязаны к полям VO, а не к RowItem

```python
# row_item_formatter.py
format_tire_diameter = format_int_or_float
format_slot_count = format_integer
```

## План миграции

1. Создать dataclass'ы в `parsers/row_item/value_objects/`.
2. Переписать `RowItem.__init__` на композицию VO.
3. Перенести `FieldDescriptor` в VO (каждому VO свои дескрипторы).
4. Переписать `to_dict()` / `from_dict()` с учётом вложенности.
5. Обновить все использования `row_item.width`, `row_item.price_opt` → `row_item.tire.width`, `row_item.pricing.price_opt`.
6. Поправить тесты.

## Критерии готовности

- [ ] `RowItem` не имеет 40 плоских полей; сгруппированы в ≤5 value objects.
- [ ] Все тесты на чтение/запись RowItem проходят.
- [ ] `to_dict()` / `from_dict()` обратимы.
- [ ] Добавление нового типа товара = новый Value Object, без изменения `RowItem`.