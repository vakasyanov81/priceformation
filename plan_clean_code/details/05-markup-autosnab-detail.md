# 05. Autosnab: политика «без наценки» — подробно

Краткая задача: [05-markup-autosnab.md](../05-markup-autosnab.md)  
Зависит от: [01-detail](01-markup-policy-detail.md)

## Суть проблемы

`Autosnab54Parser.process`:

```python
res = super().process()
for row_item in self.parsed_items:
    fill_from_title(row_item)
    row_item.price_markup = row_item.price_opt
```

Отпускная цена **равна закупу**. Это осознанная политика («продаём по опту»), спрятанная в оркестрации рядом с разбором title. JSON наценки для autosnab, если есть, на цену не влияет. `get_min_rest_count` = 0 (не отсекать малый rest) — не путать с наценкой.

Нет `round_price`: 1001.5 останется 1001.5, у других поставщиков стало бы 1010. Фикстуры это фиксируют.

`SetPercentMarkupItemAction` после process посчитает `percent_markup ≈ 0`, если `price_markup == price_opt`. Сейчас `percent_markup` в цикле не пишется.

## Подробное решение

1. Политика `IdentityMarkupPolicy`: `apply(opt, recommended) -> opt` (или `price_markup = price_opt` без округления). Не вызывать `round_price`, пока тесты не ждут десятки.

2. `Autosnab54Parser.markup_policy()` возвращает identity. Цикл в `process()` оставляет только `fill_from_title`; наценку делает общий путь (`add_price_markup` после map/filter **или** шаг pipeline в задаче 09). Пока pipeline нет — вызвать `self.add_price_markup(row_item)` в том же цикле **после** `fill_from_title`, если цена не должна зависеть от title (не зависит). Ещё лучше: наценка в базовом `process`/after, а Autosnab только title-хук — но полный вынос цикла это задача 10. Здесь минимум: убрать присвоение `price_markup = price_opt` в пользу политики.

3. Не включать карту % и РРЦ. Если `add_price_markup` на базе всегда Mim-apply, Autosnab **обязан** переопределять `markup_policy()`, иначе все позиции получат +20% и т.д.

4. Тест `test_parse_autosnab54_ru.py`: `price_markup == price_opt` по фикстурам. Узкий тест политики: opt=1234.56, recommended=2000 → markup 1234.56 (РРЦ игнорируется).

## Ожидаемый результат

- В `process()` нет `price_markup = price_opt`.
- Цифры прайса те же, **без** округления до десятков.
- Смысл «без наценки» виден в имени политики, не в побочном присвоении.

## Риски

- Случайно прогнать через `round_price` — регрессия копеек/десятков.
- Вызов базового Mim `apply` вместо identity.
- Не рефакторить `fill_from_title` в этом PR.
