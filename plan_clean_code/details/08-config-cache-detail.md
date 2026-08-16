# 08. Кэш наценки на экземпляре — подробно

Краткая задача: [08-config-cache.md](../08-config-cache.md)  
Зависит от: [07-detail](07-config-factory-detail.md)

## Суть проблемы

В `ParseConfiguration`:

```python
class ParseConfiguration:
    _markup_rules: MarkupRules | None = None
    _price_markup_map: tuple[MarkUpParams, ...] | None = None

    def __init__(...):
        self.parse_config = parse_config
        self._all_vendor_config = None  # уже instance
```

`_markup_rules` и `_price_markup_map` объявлены **на классе**. В Python присваивание `self._markup_rules = ...` создаёт атрибут экземпляра и **перестаёт** писать в класс. Первое чтение `if not self._markup_rules` идёт в класс (`None`), затем instance cache.

Проблемы:

1. **Путаница и хрупкость.** Integration-тест `test_four_tochki_real_price.py` делает `config._markup_rules = None  # noqa: WPS437` — лечит симптом «кэш не сбросить». Если когда-нибудь написать `ParseConfiguration._markup_rules = rules`, все экземпляры увидят одни правила.

2. **Ложное «not».** `if not self._markup_rules` / `if not self._price_markup_map`: пустой tuple карты — falsy, карта будет перечитываться каждый вызов. Для пустого JSON это лишний I/O; лучше `is None`.

3. **Разные vendors — разные JSON.** 12 экземпляров `ParseConfiguration`. Пока assignment на self, они не делят кэш. Регрессия возможна при рефакторинге фабрики (вернуть один singleton, кэшировать на классе). Задача фиксирует инвариант тестом.

4. `_all_vendor_config` уже instance-level — непоследовательность.

## Подробное решение

1. В `__init__`:

```python
self._markup_rules: MarkupRules | None = None
self._price_markup_map: tuple[MarkUpParams, ...] | None = None
self._all_vendor_config = None
```

Убрать class-body assignment этих двух полей (оставить только аннотации в `__init__`).

2. Условия: `if self._markup_rules is None`, `if self._price_markup_map is None`.

3. Тест: два `ParseConfiguration` с разными mock `get_markup_data` (percent 0.1 vs 0.9). После `get_price_markup_map()` у каждого свой percent. Повторный вызов не зовёт provider второй раз (`call_count == 1`).

4. Убрать сброс `_markup_rules = None` из integration-теста, если после правки тест и так изолирован (новый экземпляр конфига на прогон). Если тест **мутирует JSON на диске в процессе** — оставить явный метод `clear_cache()` на экземпляре, не лазить в private.

5. Не делать глобальный TTL и не читать файл на каждый `get` без кэша (дорого в цикле строк).

## Ожидаемый результат

- Нет class-level mutable cache для markup.
- Два поставщика в одном процессе не видят чужие правила.
- Integration FourTochki без WPS437-сброса, либо с публичным `clear_cache()`.
- Этап 2 закрыт вместе с фабрикой.

## Риски

- Существующие тесты, которые переиспользуют один `poshk_config` и ждут перечитывания файла после правки на диске — сломаются. Им нужен новый instance или `clear_cache`.
