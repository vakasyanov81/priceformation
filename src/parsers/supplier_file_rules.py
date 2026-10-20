"""Имена файлов в папке поставщика: какие читает разбор (маски `file_templates`) и как назвать прайс."""

from dataclasses import dataclass
from fnmatch import fnmatchcase
from pathlib import Path

from parsers.base_parser.warehouse_filter import TERRITORIES_FILENAME
from parsers.supplier_price_errors import SupplierPriceFileNameError
from parsers.supplier_price_sources import is_excel
from parsers.vendor_config.provider import load_vendor_configs

_PRICE_STEM = 'price'
_MAX_PRICE_NUMBER = 99
_MSG_NAME = 'Файл {name} не подходит поставщику «{folder}»: разбор читает только {expected}'
_MSG_DUPLICATE = 'Поставщику «{folder}» передано несколько файлов с именем {name}'


@dataclass(frozen=True, slots=True)
class SupplierFileRules:
    """Какие имена файлов читает разбор поставщика."""

    templates: tuple[str, ...]
    extra_names: tuple[str, ...] = ()

    def accepts(self, name: str) -> bool:
        """Имя подходит под маску поставщика или служебное имя."""
        if name in self.extra_names:
            return True
        return any(fnmatchcase(name, template) for template in self.templates)

    def is_excel_price(self, name: str) -> bool:
        """Excel-прайс, который читает разбор (кандидат на замену при новой загрузке)."""
        return is_excel(name) and self.accepts(name)

    def expected(self) -> str:
        """Перечень масок и служебных имён для сообщения об ошибке."""
        return ', '.join((*self.templates, *self.extra_names))


@dataclass(frozen=True, slots=True)
class PriceFile:
    """Файл для папки поставщика: откуда взять и под каким именем положить."""

    source: Path
    name: str


def vendor_file_rules() -> dict[str, SupplierFileRules]:
    """Правила имён файлов по папкам поставщиков: маски всех секций и служебные файлы."""
    rules: dict[str, SupplierFileRules] = {}
    for folder, config in load_vendor_configs().items():
        templates = dict.fromkeys(template for section in config.sections for template in section.file_templates)
        extra_names = (TERRITORIES_FILENAME,) if config.behavior.warehouse_cities else ()
        rules[folder] = SupplierFileRules(tuple(templates), extra_names)
    return rules


def plan_files(folder: str, rules: SupplierFileRules, sources: list[Path]) -> list[PriceFile]:
    """Назначить имена: подходящие под маски — как есть, остальные Excel — price, price_2, …"""
    planned = _kept_names(folder, [path for path in sources if rules.accepts(path.name)])
    others = [path for path in sources if not rules.accepts(path.name)]
    for other in others:
        taken = {price_file.name for price_file in planned}
        planned.append(PriceFile(other, _free_price_name(other, rules, taken, folder)))
    return planned


def _kept_names(folder: str, matching: list[Path]) -> list[PriceFile]:
    """Файлы с подходящими именами кладутся как есть; два файла с одним именем — ошибка."""
    planned: list[PriceFile] = []
    for source in matching:
        if any(price_file.name == source.name for price_file in planned):
            raise SupplierPriceFileNameError(_MSG_DUPLICATE.format(folder=folder, name=source.name))
        planned.append(PriceFile(source, source.name))
    return planned


def _free_price_name(source: Path, rules: SupplierFileRules, taken: set[str], folder: str) -> str:
    """Первое свободное имя price<N>.<ext>, которое прочитает разбор поставщика."""
    candidates = _price_names(source.suffix.lower()) if is_excel(source.name) else ()
    for name in candidates:
        if name not in taken and rules.accepts(name):
            return name
    message = _MSG_NAME.format(name=source.name, folder=folder, expected=rules.expected())
    raise SupplierPriceFileNameError(message)


def _price_names(extension: str) -> tuple[str, ...]:
    """price.<ext>, price_2.<ext>, …"""
    numbered = (f'{_PRICE_STEM}_{number}{extension}' for number in range(2, _MAX_PRICE_NUMBER + 1))
    return (f'{_PRICE_STEM}{extension}', *numbered)
