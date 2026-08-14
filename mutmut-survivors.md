# Выжившие мутанты (без логирования)

По прогону `uv run mutmut run`. Модули логирования (`log_message`, `log_resolve`, `init_log`, `wrappers`, `async_utils`) исключены из mutmut и из этого отчёта. Сюда не входят и мутации текста/`need_print_log` в `CommonPrice.parse_all_vendors` / `parse_vendor`.

Осталось **~213** содержательных выживших. Ниже — приоритет правок тестов и кода.

## 1. `test_grouper` без assert (~82 мутанта)

```python
grouper = CommonPriceGrouper([item1, item2])
grouper.get_double_row_items()
```

Тест ничего не проверяет. Из‑за этого живут `define_intimacy`, `group_key`, `clear_model`, `_is_float_diameter`, `_assign_groups`, `_assign_orders`, `_mark_double_items`, `is_double`.

**Тест:** после группировки проверить, что оба item в одной группе, `order` равен 1 и 2, дубли размечены, ключ учитывает TL / модель после дефиса / совпадение brand и manufacturer.

Отдельные юнит-тесты:

| Сценарий | Что убивает |
|---|---|
| title `"... TL ..."`, intimacy пустой → `"TL"` | `.upper()`/`.lower()`, `"tl"` → `"TL"`, `in` → `not in` |
| title без TL, `type_production="грузовая"`, diameter `"22.5"` → `"TL"` | `and` → `or`, строка `"грузовая"`, fallback `"TL"` |
| diameter `"22"` → не TL | инверсия `is_integer()` |
| `clear_model("КАМА-NU 701") == "NU701"` | `split("-")`, `len > 1` vs `> 2` |
| brand совпадает с manufacturer → brand в ключе `""` | `==` → `!=` |
| `sanitize_value([None, 1]) == ("", "1")` | `is None` → `is not None` |
| ровно 2 item в группе → оба помечены как дубли | `< 2` → `<= 2` / `< 3` |
| `order` начинается с 1 | `enumerate(..., start=2)` |

## 2. Дефолты `markup_params_from_rule` (9)

Тесты всегда передают `min` / `max` / `percent`, поэтому `get(..., 0)` → `1` / `None` не ловятся.

```python
def test_rule_defaults_when_keys_missing() -> None:
    markup = markup_params_from_rule({})
    assert markup == data_provider.MarkUpParams(min=0, max=0, percent_markup=0)
```

Также: сообщение `PriceRulesConfigFileError` при отсутствии файла; `_load_markup_json` читает путь из `get_file_path()`, а не `None`.

## 3. `prepare_str_to_float` — нет прямых тестов (11)

Docstring обещает `"<40"`, `">40"`, `"более40"`, `"1,500"`, `"руб."` — ни один кейс не покрыт.

```python
@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("<40", "40"),
        (">40", "40"),
        ("БОЛЕЕ40", "40"),
        ("1,500", "1.500"),
        ("100руб.", "100"),
    ],
)
def test_prepare_str_to_float(raw: str, expected: str) -> None:
    assert prepare_str_to_float(raw) == expected
```

Плюс `strip_into_str("1 500") == "1500"` и `get_stripped(None) == ""`.

`get_sanitized_code(123.0) == "123"` убьёт `int(field_raw)` → `None`.

## 4. Карты колонок Mim (32)

`config_for_sheets2` / `config_for_sheets3` вызываются при импорте. Тесты кормят `FakeXlsReader` уже готовыми dict — индексы колонок никто не проверяет. Сдвиг `0→1`, `22→23` выживает.

```python
def test_sheet2_column_map() -> None:
    assert config_for_sheets2()[0] == RowItem.code.name
    assert config_for_sheets2()[22] == RowItem.price_opt.name
    assert config_for_sheets2()[23] == RowItem.price_recommended.name
```

То же для sheet 3. Либо парсить реальный xlsx, а не fake dict.

**Код:** карты можно сделать константами `dict[int, str]`, а не функциями — меньше мутантов на `return None`.

## 5. Zapaska HTTP и dotenv (26)

`get_data`: `assert_called_once()` без аргументов — живут `GET` → `get`, `headers=None`, `login=None`.

```python
mock_conn.return_value.request.assert_called_once_with(
    "GET",
    "/API/hs/V2/GetTires",
    headers={"Authorization": mock.ANY},
)
```

`_parse_dotenv_line`:

- `"# KEY=val"` → `None` (убивает `startswith("#")` и `or` → `and`)
- `'KEY="quoted"'` → `quoted`
- `"KEY=a=b"` → `("KEY", "a=b")` (`partition` vs `rpartition`)

`get_zapaska_api_config`: сейчас удаляются **оба** credential. Нужен кейс «есть login, нет password» — убьёт `or` → `and`.

`load_dotenv`: путь по умолчанию `.env` (не `.ENV`); encoding `"utf-8"` можно не гонять — см. эквиваленты ниже.

`basic_auth`: проверить, что в заголовке есть `username:password` в base64. Смену `utf-8`/`ascii` на тот же codec в другом регистре не ловить.

## 6. Мелкие дыры

**black_list** — `"test1\n test2"` одинаково работает для `split("\n")` и `split(None)`. Нужна строка с пробелом внутри:

```python
assert split_and_filtration("foo bar\nbaz") == ["foo bar", "baz"]
```

**Код:** `splitlines()` вместо `split("\n")` + `strip(f" {newline}")`.

**sort_by_length** — `reverse=True` vs `False`. Алиасы разной длины, где длинный должен матчиться первым (`"BF Goodrich"` vs `"BF"`).

**manufacturer_finder** `and` → `or`: все фикстуры имеют и alias, и имя. Нужен title, где manufacturer найден, а `bad_manufacturer` пустой — `replace_alias_in_title` не должен вызываться.

**BaseFinder._find** — `find` vs `rfind`; `>` vs `>=` на длине title. Нужен alias, который встречается дважды, и title, равный алиасу по длине.

**write_all_prices** — в коде даже стоит `# TODO add test`. Проверить, что writer вызывается с `write_driver()`, `to_raw_dicts(row_items)` и шаблоном.

**CommonPrice / FieldDescriptor / XlsReader `__init__`** — тесты не проверяют, что зависимости сохраняются в атрибуты (`xls_writer`, `write_driver`, `formatter`, `name`).

**nomenclature_correction** — `from_path(file_path)` / `_read_corrections(file_path)`, а не `None`.

**all_vendor_supplier_info** — значение в словаре равно `supplier.name`, не `None`.

**parse_all_vendors** — `vendor_cls(vendor_config)`, не `vendor_cls(None)`.

## Эквиваленты — не гонять

- `"utf-8"` ↔ `"UTF-8"`, `"ascii"` ↔ `"ASCII"` (алиасы кодеков)
- `cast(...)` только для типов (`FieldDescriptor.__get__`)
- `or ""` / `or 0`, когда в фикстурах поле всегда заполнено — либо добавить пустое значение, либо не считать дырой
- `getattr(row_item, "is_double", False)` при всегда существующем поле: опечатка имени даёт default и выживает. Если поле гарантировано на `RowItem`, лучше прямое обращение.

## Порядок внедрения

1. Assert в grouper + тесты `define_intimacy` / `group_key` / `clear_model`
2. Дефолты `markup_params_from_rule`
3. `prepare_str_to_float` / `strip_into_str` / `get_sanitized_code`
4. Карты колонок Mim
5. Zapaska `request(...)` / dotenv / один отсутствующий credential
6. black_list, sort_by_length, manufacturer_finder, write_all_prices
