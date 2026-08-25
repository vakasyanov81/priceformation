# 15. HTTP-клиент Zapaska вне парсера

Подробно: [15-zapaska-http-detail.md](details/15-zapaska-http-detail.md)

Этап: [4. Слои и побочные эффекты](../PLAN_CLEAN_CODE.md#этап-4-слои-и-побочные-эффекты)  
Статус: сделана  
Зависит от: [12. JSON reader](12-parser-json-reader.md)  
Дальше: [16. Title aliases](16-parse-paths-aliases.md)

## Зачем

`get_data` / `save_data` / `load_remote_data` живут в `zapaska_tire_json.py`. Парсер JSON и клиент API в одном модуле; `all_vendors` знает про Zapaska как исключение.

## Сделать

1. Клиент вынести из `parsers/vendors` (например `src/parsers/remote/` или рядом с `cfg/zapaska_api.py`).
2. `all_vendors.load_remote_vendor_data` делегирует клиенту, не знает URL.
3. Credentials по-прежнему из env (`cfg/zapaska_api.py`).
4. Тест загрузки API без парсера прайса.

## Файлы

- `src/parsers/vendors/zapaska_tire_json.py`
- `src/parsers/all_vendors.py`
- `src/run.py`
- `src/cfg/zapaska_api.py`
- `tests/test_cfg/test_zapaska_api.py` и/или новый тест клиента

## Готово, когда

- В vendor-парсере нет `HTTPSConnection`.
- Загрузка API тестируется отдельно от разбора JSON.

## Не делать

Смена URL/контракта API, хранение пароля в JSON.
