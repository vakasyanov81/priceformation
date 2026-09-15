# Task-01: Vendor Registry

## Проблема

1. **Хардкод списка вендоров** — `all_vendors()` в `parsers/all_vendors.py` возвращает жёстко закодированный список `(класс, config)`. Добавление нового поставщика требует правки файла.
2. **Политики наценки привязаны к классам** — `_MAP_ON_OPT_VENDORS`, `_IDENTITY_VENDORS`, `_RECOMMENDED_OR_MAP_VENDORS` в `common_price.py`. Это `if`-цепи, не расширяемые без изменения кода.
3. **Конфигурация каждого вендора** — импорт `*_config` из каждого модуля в `all_vendors.py`.

## Решение

### 1. Декоратор `@register_vendor`

```python
# parsers/registry.py

_registry: dict[str, type[BaseParser]] = {}


def register_vendor(
    code: str,
    *,
    markup_policy: type[MarkupPolicy] | Literal['map_on_opt', 'identity', 'recommended_or_map'] | None = None,
    enabled_by_default: bool = True,
):
    def wrapper(cls: type[BaseParser]) -> type[BaseParser]:
        cls._vendor_code = code
        cls._markup_policy_type = markup_policy
        cls._enabled_by_default = enabled_by_default
        _registry[code] = cls
        return cls

    return wrapper
```

### 2. Парсер сам регистрируется

```python
@register_vendor('poshk', markup_policy='map_on_opt')
class PoshkParser(BaseParser):
    @classmethod
    def supplier_folder_name(cls) -> str:
        return 'poshk'

    ...
```

### 3. `all_vendors()` собирает реестр

```python
def all_vendors() -> list[VendorEntry]:
    result = []
    for code, cls in _registry.items():
        config_func = getattr(cls, 'make_config', None)
        config = config_func() if config_func else make_parse_config(cls.parser_params())
        result.append((cls, config))
    return result
```

### 4. Политика определяется атрибутом класса

```python
def _markup_policy_for_vendor(vendor_cls, vendor_config):
    policy_type = getattr(vendor_cls, '_markup_policy_type', None)
    if policy_type is None:
        return None  # default
    if policy_type == 'identity':
        return IdentityMarkupPolicy.create()
    if policy_type == 'map_on_opt':
        return make_map_on_opt_markup_policy(vendor_config)
    if policy_type == 'recommended_or_map':
        return RecommendedOrMapMarkupPolicy.from_config(vendor_config)
    # или класс:
    return policy_type(vendor_config)
```

## План миграции

1. Создать `parsers/registry.py` с декоратором и реестром.
2. В каждом вендоре навесить `@register_vendor`.
3. Переписать `all_vendors()` на сбор из реестра.
4. Удалить `_MAP_ON_OPT_VENDORS` / `_IDENTITY_VENDORS` / `_RECOMMENDED_OR_MAP_VENDORS` из `common_price.py`.
5. Перенести логику `_markup_policy_for_vendor` в `registry.py` (или `markup_policy.py`).
6. Удалить прямые импорты вендоров из `all_vendors.py`.

## Критерии готовности

- [x] Добавление нового вендора = создание класса + `@register_vendor`, **без правки** `all_vendors.py` и `common_price.py`.
- [x] `all_vendors()` возвращает тот же набор вендоров, что и до рефакторинга.
- [x] Тесты `test_all_vendors` проходят без изменений.
- [x] Старые прямые импорты вендоров удалены (кроме тех, что нужны в тестах).