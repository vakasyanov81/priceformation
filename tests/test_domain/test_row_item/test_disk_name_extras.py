"""Хвосты названия диска: нагрузка в кг различает исполнения одного диска."""

import pytest

from domain.row_item.disk_name_extras import disk_name_extras


@pytest.mark.parametrize(
    ('title', 'expected'),
    [
        ('16 Trebl 5.5*16 6*170 ЕТ105 130.1 S 1000 кг. паллета', '1000 кг'),
        ('16 Trebl 5.5*16 6*170 ЕТ105 130.1 S 1200 кг. паллета', '1200 кг'),
        ('16 Trebl 5.5*16 6*170 ET105 130.1 B (1000 кг) паллета', '1000 кг'),
        ('16 ТЗСК Gazell 5.5*16 6*170 ET105 D130 серебро 1200кг паллета', '1200 кг'),
        ('Диск штамп SRW 5.5x16 6x170 ET106 d130 Газель серебристый (8 мм) 1 350 кг', '1350 кг'),
    ],
)
def test_disk_name_extras_has_load_in_kg(title: str, expected: str) -> None:
    """Нагрузка «N кг» попадает в хвосты в одном каноне: число без пробелов и «кг»."""
    assert disk_name_extras(title) == expected


def test_disk_name_extras_ignores_dimensions_before_kg_text() -> None:
    """Диаметр ЦО и ET рядом не принимаются за нагрузку."""
    assert disk_name_extras('13 Trebl 5.0*13 4*98 ЕТ29 60.1 S паллета') == ''
