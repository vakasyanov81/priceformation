"""Описание выходных групп шаблона, независимое от настроек поставщика."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from domain.product_groups import ProductGroup

type WriteColumns = list[dict[str, Any]]
type WriteColors = dict[str, Any]
type WriteExclude = dict[str, Any]


class OutputMode(StrEnum):
    """Размещение товарных групп в книгах."""

    SEPARATE_FILES = 'separate_files'
    WORKBOOK_SHEETS = 'workbook_sheets'


@dataclass(frozen=True)
class GroupOutput:
    """Выходные колонки, фильтры и оформление одной группы."""

    id: ProductGroup
    sheet_name: str
    columns: WriteColumns
    filters: WriteExclude
    formatting: WriteColors
    merge_warehouses: bool = False
    file_name: str | None = None
    schema_version: int = 1


@dataclass(frozen=True)
class TemplateOutput:
    """Описание размещения групп; проверка выполняется до построения плана записи."""

    template_id: str
    mode: OutputMode
    groups: tuple[GroupOutput, ...]
    file_name: str | None = None
