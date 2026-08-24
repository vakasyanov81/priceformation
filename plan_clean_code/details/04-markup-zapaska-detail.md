# 04. Zapaska: наценка в JSON — подробно

Краткая задача: [04-markup-zapaska.md](../04-markup-zapaska.md)  
Зависит от: [01-detail](01-markup-policy-detail.md)  
Статус: сделана

## Суть проблемы

Zapaska (диски и шины через `ZapaskaDiskJSON.make_price_markup`) **не** использует `zapaska_markup_rules.json` для расчёта. Правила зашиты в `zapaska_disk_markup.py`:

| Закуп `price_opt` | Доля наценки |
| --- | --- |
| [0, 5000) | 0.22 |
| [5000, 10000) | 0.20 |
| [10000, 15000) | 0.16 |
| [15000, 20000) | 0.14 |
| [20000, 25000) | 0.12 |
| ≥ 25000 | 0.12 (`_BASE_PERCENT`) |

Дополнительно:

- Если РРЦ есть и маржа **> 8%** (`MIN_RECOMMENDED_MARGIN_PERCENT = 0.08`, сравнение `<=` на пороге → 8% считается «мало») — отпускная = РРЦ.
- Если РРЦ есть и маржа ≤ 8% — отпускная = `opt * (1 + map%)`.
- Если РРЦ нет — сразу `opt * (1 + map%)`.
- Затем абсолютный пол: если `price - opt <= 150` (`_ABSOLUTE_MARKUP_DELTA`), цена = `opt + 150`.

Отличия от Mim/`MarkupPolicy` задачи 01:

- границы полок **полуинтервалы** `[min, max)`, не `min <= x <= max` (в базе оба конца включены, полки в JSON ещё и пересекаются);
- порог РРЦ 8% vs `min_recommended_percent_markup` в JSON Mim;
- абсолют — **рублёвая дельта +150**, не `opt * markup_percent` как в `absolute_markup_rules`;
- нет `max_recommended`.

Пока это в Python, бизнес не может сменить 17%/15%/… без релиза. Тесты (`test_zapaska_disk_markup.py`) привязаны к приватным `_get_price_percent_markup` и константам — сигнал, что модуль и есть политика.

`make_price_markup` в парсере: при пустом opt — return; при пустой РРЦ пишет title в `not_matched_position` (побочный список, на цену не влияет); округление `round_price` после `make_price_markup_value`; если value falsy — `price_markup = None`.

## Подробное решение

1. Описать правила в JSON Zapaska так, чтобы **тот же** движок политики их читал, либо расширить JSON полями, которых нет у Mim.

   Вариант A (предпочтительный для одной политики): расширить схему `markup_rules.json`:

   - полки как сейчас `min/max/percent`, но задать **соглашение о границах** (включительно/исключительно) одним флагом на файл, например `"interval": "right_open"`;
   - `min_recommended_percent_markup: 0.08`;
   - абсолют: либо новый ключ `"min_absolute_delta": 150` (прибавка к opt), либо эмулировать дельту через существующие поля **нельзя** (`markup_percent` — множитель). Для Zapaska нужен **delta**, не множитель.

   Вариант B: Zapaska остаётся отдельным `ZapaskaMarkupPolicy`, но **числа только из JSON**. Python без `_BASE_PERCENT`, без словаря полок. Это слабее по DRY, но безопаснее для Mim.

   Рекомендация: общая `MarkupPolicy` с параметрами `interval`, `absolute_mode: multiplier | delta`. Mim: closed interval + multiplier. Zapaska: right-open + delta. Не ломать Mim-фикстуры.

2. Перенести числа в `parse_config/zapaska_markup_rules.json` (+ example в tests/integration_tests). Пример полок:

   ```json
   {
     "markup_rules": {
       "r22": {"min": 0, "max": 5000, "percent": 0.22},
       "r20": {"min": 5000, "max": 10000, "percent": 0.20},
       "r16": {"min": 10000, "max": 15000, "percent": 0.16},
       "r14": {"min": 15000, "max": 20000, "percent": 0.14},
       "r12": {"min": 20000, "max": 25000, "percent": 0.12}
     },
     "interval": "right_open",
     "min_recommended_percent_markup": 0.08,
     "absolute_markup_rules": {
       "min_absolute_markup": 150,
       "mode": "delta"
     }
   }
   ```

   Полка ≥25000: как сейчас fallback `_BASE_PERCENT` 0.12 — либо правило с большим max, либо default_percent = 0.12 явно.

3. Порог 8%: в коде `_is_small_recommended_price` использует `<= percent`. Mim: `< min_recommended`. Сохранить `<=` для Zapaska (тест: РРЦ=1080 при opt=1000 → small). Параметр `recommended_cmp: "lt" | "le"`.

4. Удалить публичную логику из `zapaska_disk_markup.py` или оставить тонкий deprecated-wrapper для тестов на один релиз, затем стереть. Парсер вызывает `MarkupPolicy.apply`.

5. Переписать `test_zapaska_disk_markup.py` на политику + JSON (не импорт `_get_price_percent_markup`). Параметризация полок из таблицы выше должна остаться зелёной. Parse-тесты disk/tire — те же `price_markup`.

6. Шины (`ZapaskaTireJSON`) наследуют `make_price_markup` дисков — один перенос покрывает оба.

## Ожидаемый результат

- В Python нет 0.22/0.20/…, 0.08, 150 как бизнес-констант наценки.
- Таблица тестов полок и absolute floor (1100→1150 при opt=1000) зелёная.
- Фикстуры parse disk/tire без изменения цен.
- Смена полки — правка JSON.

## Риски

- Смешать closed и right-open: opt=5000 сейчас 0.20, при `<= max` первой полки (0–5000) стал бы 0.22.
- `mode: delta` vs Mim `markup_percent: 1.3` — разные семантики одного NamedTuple; не подставить delta в Mim.
- `price_markup = None` при falsy — сохранить, если фикстуры на это завязаны.
- HTTP и JSON reader — не эта задача.
