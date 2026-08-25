# 17. Предсказуемые кэши процесса — подробно

Краткая задача: [17-process-caches.md](../17-process-caches.md)  
Зависит от: [08-detail](08-config-cache-detail.md)  
Статус: сделана

## Суть проблемы

Два модуля кэшируют данные с диска на **процесс**, без явного сброса.

### nomenclature_correction

```python
class _NomenclatureCache:
    titles: dict[str, str] | None = None

def get_nomenclature_corrected_title(title: str) -> str:
    if _NomenclatureCache.titles is None:
        _NomenclatureCache.titles = load_file()
    return cache.get(title) or title
```

`CommonPriceOut.write_all_prices` перед записью правит **все** title. Первый вызов в процессе читает `parse_config/correct-nomenclature.xlsx`. Правка xlsx без рестарта процесса **не видна**. Тесты, пишущие разные файлы номенклатуры, заражают друг друга, если не изоляция процесса.

### manufacturer_aliases.load_aliases_map

```python
@lru_cache(maxsize=1)
def load_aliases_map() -> dict[str, Any]:
    try:
        return ManufacturerAliasesProviderFromUserConfig().get_aliases()
    except FileNotFoundError:
        return {}
```

`group_key` / grouping может звать это, даже если парсеру передали aliases в `ParseConfiguration`. Второй набор данных: конфиг парсера vs глобальный кэш. `CommonPriceGrouper(aliases_map=None)` тогда читает диск через cache.

`drop_blank_aliases` чистый; кэш именно I/O.

Связка с задачей 08: там кэш **экземпляра конфига**; здесь — модуль. Один процесс `run.py` в цикле меню: пользователь правит aliases/номенклатуру, жмёт «сформировать прайс» снова — увидит старые данные. Для CLI это реальный баг.

## Подробное решение

1. Публичные `clear_nomenclature_cache()` и `load_aliases_map.cache_clear()` (или обёртка `clear_manufacturer_aliases_cache()`).

2. Вызывать сброс в начале `CommonPrice.parse_all_vendors` и/или `CommonPriceOut.write_all_prices` — **один раз на прогон прайса**, не на каждую строку. Тогда повтор в меню подхватит файлы.

3. Альтернатива жёстче: не кэшировать между прогонами, кэшировать только внутри одного `write_all_prices` локальной переменной. Для xlsx номенклатуры (~один read) это дёшево. Для aliases grouping — тоже один read на прогон, передать `aliases_map` в `CommonPriceGrouper` из конфига **одного** vendor или общего provider, не `load_aliases_map()` из group_key.

   Предпочтение: `group_key` / grouper получают map аргументом; `load_aliases_map` остаётся удобным дефолтом с cache_clear на старте прогона.

4. Тесты: заполнить кэш значением A, сменить mock файла / сбросить, получить B. Тест «два write_all_prices без сброса» документирует выбранную семантику (со сбросом на прогон — B).

5. Не выносить в БД.

## Ожидаемый результат

- Повтор «сделать прайс» в одном процессе видит обновлённые `correct-nomenclature.xlsx` и `manufacturer_aliases.json`.
- Тесты не зависят от порядка из-за чужого кэша (сброс в фикстуре conftest или на старте прогона).
- Нет чтения xlsx на каждую из N строк (кэш внутри прогона остаётся).

## Риски

- Сброс каждый `get_nomenclature_corrected_title` — катастрофа по I/O. Только на границе прогона.
- `lru_cache` на `load_aliases_map` ключей не имеет — первый FileNotFound закэширует `{}` навсегда даже после появления файла. Сброс на прогон это лечит.
