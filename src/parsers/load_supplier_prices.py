"""Загрузка файлов прайсов поставщиков в file_prices.

Поставщику можно передать один файл, несколько файлов или zip-архив с ними. Имя файла в папке
поставщика определяет, прочитает ли его разбор (маски `file_templates`), поэтому:

- файл, имя которого уже подходит под маску поставщика или служебное имя (`territories.json`
  при фильтре складов), сохраняет имя;
- остальные xls/xlsx получают имя `price.<расширение>` (следующие — `price_2`, `price_3`, …),
  если такое имя подходит под маски поставщика;
- прочие файлы — ошибка: разбор их не увидит.

Старые файлы: одноимённые заменяются; если пришли xls/xlsx, прежние Excel-прайсы поставщика
(подходящие под его маски) удаляются, чтобы в разбор не попал устаревший набор.
Все файлы проверяются до первого перемещения: при ошибке папки поставщиков не меняются.
"""

import json
from collections.abc import Mapping
from pathlib import Path

from domain.protocols import ConfigProvider
from parsers.all_vendors import all_vendor_supplier_catalog
from parsers.supplier_file_rules import plan_files, vendor_file_rules
from parsers.supplier_price.errors import SupplierPricesMappingError, UnknownSupplierCodeError
from parsers.supplier_price.placement import SupplierUpload, place_files
from parsers.supplier_price.sources import PriceSources, expand_sources, unpacked_dir

_MSG_MAPPING = 'Ожидается объект {ид_или_код_поставщика: путь_к_файлу или список путей}'
_MSG_NONEMPTY = 'Ключ поставщика и пути к файлам должны быть непустыми строками'
_MSG_UNKNOWN = 'Неизвестный ИД или код поставщика: {0}'


def parse_prices_json(raw: str) -> dict[str, PriceSources]:
    """Разобрать JSON-объект ИД или sup_code → путь к файлу или список путей."""
    try:
        loaded: object = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SupplierPricesMappingError(str(exc)) from exc
    if not isinstance(loaded, dict):
        raise SupplierPricesMappingError(_MSG_MAPPING)
    if not all(isinstance(key, str) and key for key in loaded):
        raise SupplierPricesMappingError(_MSG_NONEMPTY)
    return {key: _mapping_paths(paths) for key, paths in loaded.items()}


def _mapping_paths(paths: object) -> PriceSources:
    """Путь строкой или непустой список непустых строк (кортежем)."""
    if isinstance(paths, str) and paths:
        return paths
    path_list = paths if isinstance(paths, list) else []
    if path_list and all(isinstance(path, str) and path for path in path_list):
        return tuple(path_list)
    raise SupplierPricesMappingError(_MSG_NONEMPTY)


def load_supplier_prices(mapping: Mapping[str, PriceSources], config_provider: ConfigProvider) -> list[str]:
    """Разложить файлы по папкам поставщиков; вернуть пути положенных файлов."""
    targets = _supplier_folders(mapping, config_provider)
    with unpacked_dir() as unpack_dir:
        uploads = [_plan_upload(folder, sources, unpack_dir, config_provider) for folder, sources in targets]
        return [dest for upload in uploads for dest in place_files(upload, config_provider)]


def catalog_entry_for(
    supplier_key: str,
    catalog: dict[str, dict[str, str]],
) -> dict[str, str]:
    """Запись каталога по ИД поставщика или sup_code."""
    by_id = catalog.get(supplier_key)
    if by_id is not None:
        return by_id
    for entry in catalog.values():
        if entry['sup_code'] == supplier_key:
            return entry
    raise UnknownSupplierCodeError(_MSG_UNKNOWN.format(supplier_key))


def _supplier_folders(
    mapping: Mapping[str, PriceSources], config_provider: ConfigProvider
) -> list[tuple[str, PriceSources]]:
    """Папка поставщика для каждого ключа; неизвестный ключ — ошибка до проверки файлов."""
    catalog = all_vendor_supplier_catalog(config_provider)
    folders = [catalog_entry_for(key, catalog)['sup_code'] for key in mapping]
    return list(zip(folders, mapping.values(), strict=True))


def _plan_upload(
    folder: str, sources: PriceSources, unpack_dir: Path, config_provider: ConfigProvider
) -> SupplierUpload:
    rules = vendor_file_rules(config_provider)[folder]
    files = plan_files(folder, rules, expand_sources(sources, unpack_dir))
    return SupplierUpload(folder, rules, files)
