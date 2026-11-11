"""Преобразователь второй модели только для тестов группового вывода."""

from dataclasses import dataclass

from domain.product_group_handler import OutputFields
from parsers.writer.templates.group_output import GroupOutput
from tests.test_domain.group_handler_examples import TestGroupResult


@dataclass(frozen=True)
class OtherOutputSource:
    """Метка тестовой модели не имеет шинных полей или правил дублей."""

    package: TestGroupResult

    @property
    def fields(self) -> frozenset[str]:
        return frozenset(('label',))

    def prepare(self, _template_id: str, settings: GroupOutput) -> tuple[OutputFields, ...]:
        return tuple(
            {'label': position.label}
            for position in self.package.positions
            if position.label not in settings.filters.get('label', ())
        )
