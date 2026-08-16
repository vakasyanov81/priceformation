# 06. Очистка BaseParser и контракт JSON — подробно

Краткая задача: [06-markup-cleanup.md](../06-markup-cleanup.md)  
Зависит от: [02](02-markup-poshk-pioner-detail.md), [03](03-markup-stk-detail.md), [04](04-markup-zapaska-detail.md), [05](05-markup-autosnab-detail.md)

## Суть проблемы

После 01–05 наценка должна жить в политиках. Остаточный долг:

1. **FourTochki sheet1** в исходном плане этапа 1 не вынесен отдельно, но у него свой `add_price_markup`: РРЦ если есть, иначе карта %. Это четвёртая формула рядом с Mim/map-on-opt/identity/Zapaska. Пока override жив, «единая политика» не закрыта. В этой задаче **обязательно** перевести FourTochki на политику `recommended_or_map` (без absolute/min-max Mim), иначе grep по `add_price_markup` не очистится.

2. `BaseParser.add_price_markup` может остаться тонким делегатом — это нормально. Ненормально: мёртвые `is_small_recommended_percent` и компания на классе, дублирующие политику.

3. JSON-ключ: README и example-файлы используют `"percent"`. Код принимает и `percent_markup` (`markup_params_from_rule`). Контрактный тест `test_markup_rules_contract.py` уже грузит example Mim/FourTochki/Poshk. Нужно явно зафиксировать оба ключа и запретить регресс (тест на dict `{"min","max","percent"}` и `{"percent_markup"}`).

4. Vendors могут всё ещё содержать локальные формулы (`1.06`, `_percent_map`, `(percent + 1) * price`).

## Подробное решение

1. Инвентаризация `grep -n add_price_markup src tests`. Ожидание: определения только в `BaseParser` (делегат) и, возможно, ни одного override. FourTochki sheet1 — перевести на политику:

   - если `price_recommended` — она;
   - иначе `get_markup(opt, map%)`;
   - `round_price`;
   - **без** absolute floor Mim (иначе изменятся цены Форточек).

2. Удалить с `BaseParser` методы, ставшие обёртками политики, если нет внешних вызовов. Оставить `round_price`, если им пользуются не только наценка (да, vendors). `calc_percent` / `get_markup` на классе с `lru_cache` — прокси в `price_markup.py`; кэш на float можно убрать как шум.

3. Контракт:

   - example JSON с `"percent"` → тот же `MarkUpParams`, что `"percent_markup"`;
   - приоритет, если оба ключа: как сейчас в `markup_params_from_rule` — сначала `percent_markup`, иначе `percent`. Зафиксировать тестом, не менять молча.

4. `grep` по `src/parsers/vendors`: нет `_percent_map`, `STK_PRICE_MARKUP`, `* 1.06`, ручного `(markup_percent + 1)`.

5. Документация: `README_MarkupRules.md` — оба ключа допустимы, канон для новых файлов `percent` (как в README) **или** `percent_markup`; одно решение записать.

## Ожидаемый результат

- Этап 1 закрыт: формулы наценки не в vendor-классах.
- Смена `%` STK/Zapaska/Poshk — JSON.
- Контракт percent/percent_markup зелёный на example-файлах.
- FourTochki sheet1 ведёт себя как сейчас (РРЦ приоритетнее карты).

## Риски

- Забыть FourTochki — этап 1 формально закрыт в плане, фактически нет.
- Включить Mim-absolute на Форточки.
- Поменять приоритет ключей JSON — сломать файлы с обоими полями.
