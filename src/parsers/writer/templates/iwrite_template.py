"""
write template interface
"""

from copy import deepcopy
from typing import Any, ClassVar

from domain.product_groups import ProductGroup
from parsers.writer.templates import group_output
from parsers.writer.templates.column_template import TemplateColumns

type WriteColumns = group_output.WriteColumns
type WriteColors = group_output.WriteColors
type WriteExclude = group_output.WriteExclude

# Настройки, которые шаблон задаёт классом. Имена в __COLUMNS__-стиле придуманы
# исторически, но новые опечатки в них ловятся на импорте, а не на записи
# файла: см. IWriteTemplate.
DEFAULT_TEMPLATE_FILE = 'default_result.xls'
EMPTY_COLUMN = 'empty_column'


class IWriteTemplate(TemplateColumns):
    """interface for writing template

    Настройки объявлены явно, с пустыми дефолтами: подкласс, который задал
    `__COLUMNS__` с опечаткой, падает на импорте (нет такого поля), а не
    молча пишет файл без колонок.
    """

    template_id: ClassVar[str] = 'default'

    __EMPTY_COLUMN__ = EMPTY_COLUMN

    __FILE__: ClassVar[str] = DEFAULT_TEMPLATE_FILE
    __EXCLUDE__: ClassVar[WriteExclude] = {}
    __COLOR__: ClassVar[WriteColors] = {}
    __MERGE_WAREHOUSES__: ClassVar[bool] = False

    """ write template interface """

    def exclude(self) -> dict[str, Any]:
        """get exclude"""
        return dict(self.__EXCLUDE__)

    def get_file_name(self) -> str:
        """get file name pattern"""
        return self.__FILE__

    def colors(self) -> dict[str, Any]:
        """get colors"""
        return dict(self.__COLOR__)

    def output_spec(self) -> group_output.TemplateOutput:
        """Описать текущий шинный шаблон для группового плана записи.

        Копии вложенных настроек принадлежат описанию и не меняют шаблон.
        Многогрупповой шаблон переопределяет этот метод.
        """
        group = group_output.GroupOutput(
            id=ProductGroup.TIRE_AND_DISK,
            sheet_name='price',
            columns=deepcopy(self.columns()),
            filters=deepcopy(self.exclude()),
            formatting=deepcopy(self.colors()),
            merge_warehouses=self.__MERGE_WAREHOUSES__,
            file_name=self.get_file_name(),
        )
        return group_output.TemplateOutput(self.template_id, group_output.OutputMode.SEPARATE_FILES, (group,))
