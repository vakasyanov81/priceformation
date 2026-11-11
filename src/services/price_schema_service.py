"""Контроль схемы прайсов при обновлении: копия до, сравнение после, понятные предупреждения."""

from __future__ import annotations

import logging
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from python_calamine import CalamineError

from domain.config_context import get_config_provider
from domain.protocols import ConfigProvider
from infrastructure.data.price_backup import backup_prices, default_backup_folder
from parsers.price_schema.diff import compare_schemas
from parsers.price_schema.models import FileHead, PriceSchema
from parsers.price_schema.schema import build_schema, read_file_head
from parsers.vendor_config.group_models import BatterySection
from parsers.vendor_config.models import VendorConfig
from parsers.vendor_config.provider import load_vendor_configs
from parsers.vendor_config.section_models import VendorSection

logger = logging.getLogger(__name__)


class PriceSchemaService:
    """Сравнивает шапки прайсов поставщиков до и после обновления файлов."""

    def __init__(self, backup_folder: Path | None = None, config_provider: ConfigProvider | None = None) -> None:
        """`backup_folder` — куда класть копию (по умолчанию временная папка ОС); `config_provider` — пути окружения."""
        self._config_provider = config_provider
        self._backup = backup_folder or default_backup_folder()
        self._depth = 0
        self._copied = False

    def _provider(self) -> ConfigProvider:
        """Явно переданный провайдер или активный в момент вызова."""
        return self._config_provider or get_config_provider()

    def snapshot(self) -> bool:
        """Скопировать file_prices (кроме result) в папку копии; не вышло — предупреждение и False."""
        provider = self._provider()
        skip = Path(provider.result_folder())
        try:
            backup_prices(Path(provider.price_folder('')), self._backup, skip=skip)
        except OSError as exc:
            logger.warning(f'Не удалось сделать копию прайсов ({exc}): схемы прайсов не будут сравнены.')
            return False
        return True

    @contextmanager
    def guard(self) -> Generator[None]:
        """Копия до блока, сравнение после (и после сбоя обновления); вложенные блоки работают как внешний."""
        if self._depth == 0:
            self._copied = self.snapshot()
        self._depth += 1
        try:
            yield
        finally:
            self._depth -= 1
            if self._depth == 0 and self._copied:
                self.check()

    def check(self) -> list[str]:
        """Сравнить схемы прайсов копии и текущих файлов; предупреждения выводятся в лог и возвращаются."""
        warnings: list[str] = []
        heads: dict[Path, FileHead | None] = {}
        for vendor in load_vendor_configs(self._provider()).values():
            warnings.extend(self._vendor_warnings(vendor, heads))
        for warning in warnings:
            logger.warning(warning)
        return warnings

    def _sections(self, vendor: VendorConfig) -> Generator[VendorSection | BatterySection]:
        """Секции всех объявленных групп без смешивания моделей настроек."""
        for group in vendor.product_groups:
            yield from group.sections

    def _vendor_warnings(self, vendor: VendorConfig, heads: dict[Path, FileHead | None]) -> list[str]:
        """Расхождения схем всех секций поставщика; повторы (секции на один файл) убираются."""
        warnings: dict[str, None] = {}
        for section in self._sections(vendor):
            for path in _section_files(vendor.folder, section, self._provider()):
                old_path = self._backup / vendor.folder / path.name
                for change in _file_changes(old_path, path, section, heads):
                    warnings[_message(vendor, section, path, change)] = None
        return list(warnings)


def _file_changes(
    old_path: Path,
    new_path: Path,
    section: VendorSection | BatterySection,
    heads: dict[Path, FileHead | None],
) -> list[str]:
    """Расхождения одного файла; нет копии или файл не читается — нечего сравнивать."""
    if not old_path.is_file():
        return []
    old_head, new_head = _head(old_path, heads), _head(new_path, heads)
    if old_head is None or new_head is None:
        return []
    return compare_schemas(_schema(old_head, section), _schema(new_head, section), _columns(section))


def _head(path: Path, heads: dict[Path, FileHead | None]) -> FileHead | None:
    """Шапка файла с кэшем на время проверки; нечитаемый файл — None."""
    if path not in heads:
        try:
            heads[path] = read_file_head(path)
        except (OSError, ValueError, CalamineError) as exc:
            logger.debug(f'Схема {path.name} не прочитана: {exc}')
            heads[path] = None
    return heads[path]


def _schema(head: FileHead, section: VendorSection | BatterySection) -> PriceSchema:
    """Схема файла для секции."""
    return build_schema(
        head, start_row=section.start_row, sheet_indexes=section.sheet_indexes, columns=_columns(section)
    )


def _section_files(folder: str, section: VendorSection | BatterySection, config_provider: ConfigProvider) -> list[Path]:
    """Файлы секции в file_prices/<folder> по её шаблонам."""
    root = Path(config_provider.price_folder(folder))
    found = {path for template in section.file_templates for path in root.glob(template)}
    return sorted(path for path in found if path.is_file())


def _message(vendor: VendorConfig, section: VendorSection | BatterySection, path: Path, change: str) -> str:
    """Предупреждение для пользователя."""
    location = f'{vendor.folder}/{path.name}'
    group = section.product_group
    return (
        f'Поставщик «{section.name}» ({location}), '
        f'группа «{group.display_name}» ({group.value}): '
        f'изменилась схема прайса — {change}'
    )


def _columns(section: VendorSection | BatterySection) -> dict[int | str, str]:
    """У объявленных аккумуляторов пока нет модели колонок; проверяются только листы."""
    return section.columns if isinstance(section, VendorSection) else {}
