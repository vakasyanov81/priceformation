# 15. HTTP-клиент Zapaska вне парсера — подробно

Краткая задача: [15-zapaska-http.md](../15-zapaska-http.md)  
Зависит от: [12-detail](12-parser-json-reader-detail.md)  
Статус: сделана

## Суть проблемы

В `zapaska_tire_json.py` рядом с парсером шин:

- `basic_auth` / `get_data` — `HTTPSConnection(host)`, заголовок Basic, `GET` URL, `read().decode`;
- `save_data` — путь `init_cfg().main.project_root / folder_file_prices / zapaska / filename`;
- `load_remote_data` — `GetTires` → `tire.json`, `GetDisk` → `disk.json`.

`all_vendors.load_remote_vendor_data` импортирует и зовёт только это. Меню `run.py` → «обновить данные Запаски». Парсер прайса **не** должен знать HTTP, URL и запись файлов.

Сейчас `from cfg import init_cfg` и `from cfg.zapaska_api import get_zapaska_api_config` внутри **vendor-пакета**. Credentials уже правильно в env (задача секретов закрыта); слой всё равно дырявый.

Клиент нельзя тестировать без парсера и без реального хоста, пока он в том же модуле, что `ZapaskaTireJSON`.

## Подробное решение

1. Новый модуль вне `vendors/`, например `src/parsers/remote/zapaska_client.py` **или** `src/cfg/zapaska_client.py`. Предпочтительнее `parsers/remote/` (адаптер) + credentials остаются в `cfg/zapaska_api.py`.

2. API клиента:

```python
def download_catalogs(*, dest_dir: Path, api: ZapaskaApiConfig | None = None) -> None:
    """GET GetTires / GetDisk → dest_dir/tire.json, disk.json"""
```

`dest_dir` = `Path(get_parse_paths().file_prices_folder) / "zapaska"`, не `init_cfg().main`.

3. `get_data` принимает `ZapaskaApiConfig` (уже так). Не хардкодить host: `get_zapaska_api_config()`.

4. `all_vendors.load_remote_vendor_data` → вызов клиента. `run.py` может звать клиента напрямую; тогда `all_vendors` не знает URL. Лучше: `run.py` → `load_remote_vendor_data()` в remote-пакете, `all_vendors` без HTTP.

5. Удалить HTTP и `save_data` из `zapaska_tire_json.py`. Парсер только читает json ридером (задача 12).

6. Тесты: mock `HTTPSConnection` или инъекция `get_fn`; проверка путей записи в tmpdir; ошибка без `ZAPASKA_API_LOGIN` — уже `ZapaskaApiConfigError`. Не ходить в сеть в CI.

7. Таймауты/закрытие connection: сейчас `connection` не в `try/finally`. При переносе — закрывать (`finally: connection.close()`), это часть аккуратного клиента, не смена протокола.

## Ожидаемый результат

- В `src/parsers/vendors/` нет `HTTPSConnection`, `init_cfg`, URL `/API/hs/V2/...`.
- Меню «обновить Запаску» пишет те же `tire.json`/`disk.json` в ту же папку.
- Юнит-тест клиента без `ZapaskaTireJSON`.
- Env-credentials без изменения.

## Риски

- Кодировка ответа и бинарность — сохранить `decode("utf-8")`.
- Папка zapaska может не существовать — `save_data` сейчас откроет файл и упадёт; клиент делает `mkdir(parents=True, exist_ok=True)`.
- Не логировать password.
