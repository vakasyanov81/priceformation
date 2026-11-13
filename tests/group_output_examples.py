"""Преобразователь второй модели только для тестов группового вывода."""

from dataclasses import dataclass
from pathlib import Path

from domain.product_group_handler import OutputFields
from parsers.writer.group_files import GroupFileWriter
from parsers.writer.templates.group_output import GroupOutput
from parsers.writer.xls_writer import XlsWriter
from parsers.writer.xlsxwriter_adapter import XlsxWriterAdapter
from tests.test_domain.group_handler_examples import TestGroupResult


@dataclass(frozen=True)
class OtherOutputSource:
    """Метка тестовой модели не имеет шинных полей или правил дублей."""

    package: TestGroupResult

    @property
    def fields(self) -> frozenset[str]:
        return frozenset(('label',))

    @property
    def title_fields(self) -> frozenset[str]:
        return frozenset(())

    def prepare(self, _template_id: str, settings: GroupOutput) -> tuple[OutputFields, ...]:
        return tuple(
            {'label': position.label}
            for position in self.package.positions
            if position.label not in settings.filters.get('label', ())
        )


def group_writer(folder: Path) -> GroupFileWriter:
    """Рабочие писатель и драйвер без подмены файлового IO."""
    return GroupFileWriter(xls_writer=XlsWriter, write_driver=XlsxWriterAdapter, result_folder=str(folder))
