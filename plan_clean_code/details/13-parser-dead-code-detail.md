# 13. Мёртвый Command, контракт title, Пионер — подробно

Краткая задача: [13-parser-dead-code.md](../13-parser-dead-code.md)  
Зависит от: [10-detail](10-parser-hooks-detail.md)
Статус: сделана

## Суть проблемы

Три хвоста после разрезания парсера.

### 1. Command без армии

```python
_item_actions: list[type[BaseItemAction]] = []
_item_actions_after_process = [SetPercentMarkupItemAction]
```

`_item_actions` нигде не итерируется (только объявление). `BaseItemAction.action` — NotImplemented. Живой только `SetPercentMarkupItemAction`: если нет `percent_markup` и есть `price_markup`, пишет `(markup/opt - 1)*100`. Poshk/Pioner часто уже записали percent сами — action no-op.

Держать пакет `base_item_actions` ради одного post-step — шум. Либо встроить расчёт percent в шаг markup, либо оставить **один** вызов без пустого `_item_actions`.

### 2. LSP на title

`BaseParser.get_prepared_title` — **classmethod**. Zapaska:

```python
def get_prepared_title(self, row_item: RowItem) -> str:  # type: ignore[override]
    ...
    return self.title_aliases.get(title) or title
```

Нужен instance (`title_aliases`). Mim/FourTochki — classmethod, title из полей строки. `set_prepared_title` зовёт `self.get_prepared_title` — у classmethod сработает и так, у instance — только как instance method. Mypy ругается, отсюда ignore. Контракт должен быть instance method везде (`def get_prepared_title(self, row_item)`); Mim/FourTochki могут не использовать `self`.

### 3. Двойной ManufacturerFinder у Пионера

`_enrich_row_item` уже делает `ManufacturerFinder(...).process(row_item)`. `PionerParser.process` вызывает его **снова** после `set_manufacturer_to_title`. Второй проход может переписать brand/title ещё раз. Нужно сравнить фикстуры: если второй проход меняет результат — оставить **один** осознанный момент (после вставки имени в title). Если нет — удалить вызов в `process`.

Плюс мёртвые поля Zapaska (`price_mrp_result`, `price_sup_codes`, …) — проверить vulture/тестами; если мёртвые, удалить здесь, не в 10.

## Подробное решение

1. Удалить `_item_actions` и неиспользуемый цикл, если появится. `do_items_actions_after_process` упростить до вызова percent **или** перенести в `MarkupPolicy`/pipeline «заполнить percent если пусто». Не раздувать новый фреймворк actions.

2. Сменить сигнатуру `get_prepared_title` на instance method в базе, Mim, FourTochki, Zapaska. Снять `type: ignore`. Обновить тесты, которые зовут `Cls.get_prepared_title(row)`.

3. Пионер: тест «finder один раз» — mock/счётчик или сравнение title до/после удаления второго вызова. Скорее всего второй вызов нужен **после** `set_manufacturer_to_title` (бренд появился в title). Тогда **убрать finder из enrich для Пионера** (хук) или убрать ранний enrich finder, оставив поздний — не два.

4. `uv run vulture` после удалений.

## Ожидаемый результат

- Нет пустого `_item_actions`.
- Нет `type: ignore[override]` на title.
- Пионер: один проход finder в осмысленной точке; фикстуры те же.
- Этап 3 закрыт вместе с 09–12.

## Риски

- Перенос percent в политику изменит округление vs action — сверить Poshk.
- Смена classmethod→instance сломает вызовы в тестах `FourTochkiParser1Sheet.get_prepared_title(item)`.
