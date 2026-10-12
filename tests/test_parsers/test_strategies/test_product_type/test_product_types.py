"""Словарь канонических типов и сверка заявленного типа (README §1, §7)."""

from __future__ import annotations

import pytest

from parsers.strategies.product_types import (
    CAMERA,
    CANONICAL_TYPES,
    DISK,
    LIGHT_TRUCK,
    MOTO,
    O_RING,
    PASSENGER,
    RIM_TAPE,
    SPECIAL,
    TRUCK,
    canonical_declared,
    declared_matches,
)


@pytest.mark.parametrize(
    ('declared', 'expected'),
    [
        ('Легковая', PASSENGER),
        ('Легковая шина', PASSENGER),
        ('SUV', PASSENGER),
        ('Грязевая', PASSENGER),
        ('Легкогрузовая', LIGHT_TRUCK),
        ('Легкогрузовая шина', LIGHT_TRUCK),
        ('C', LIGHT_TRUCK),
        ('LT', LIGHT_TRUCK),
        ('Грузовая', TRUCK),
        ('Грузовая шина', TRUCK),
        ('Груз.', TRUCK),
        ('Спецтехника', SPECIAL),
        ('Сельхоз', SPECIAL),
        ('Индустриальная', SPECIAL),
        ('Спецшина', SPECIAL),
        ('Мото', MOTO),
        ('Мотошина', MOTO),
        ('Автокамера', CAMERA),
        ('Камера', CAMERA),
        ('Диск', DISK),
        ('Ободная лента', RIM_TAPE),
        ('Флиппер', RIM_TAPE),
        ('Уплотнительное кольцо', O_RING),
    ],
)
def test_canonical_declared_known(declared: str, expected: str) -> None:
    """Конкретные ярлыки поставщиков канонизируются по таблице README §7."""
    assert canonical_declared(declared) == expected


@pytest.mark.parametrize(
    'declared',
    [None, '', '  ', 'Автошина', 'Шина', 'Автопокрышка', 'Прочие', 'Марсианская'],
)
def test_canonical_declared_generic_or_unknown(declared: str | None) -> None:
    """Общие и неизвестные ярлыки не канонизируются (нет сравнения)."""
    assert canonical_declared(declared) is None


@pytest.mark.parametrize(
    ('declared', 'own', 'expected'),
    [
        ('Грузовая шина', SPECIAL, False),
        ('Легкогрузовая', PASSENGER, False),
        ('Спецшина', TRUCK, False),
        ('Грузовая', TRUCK, True),
        ('SUV', PASSENGER, True),
        ('Автошина', SPECIAL, True),
        ('Прочие', SPECIAL, True),
        ('Марсианская', SPECIAL, True),
        ('', SPECIAL, True),
        (None, SPECIAL, True),
        ('Грузовая', '', True),
    ],
)
def test_declared_matches(declared: str | None, own: str, expected: bool) -> None:
    """Расхождения нет при пустом своём типе, общем/неизвестном или совпадении."""
    assert declared_matches(declared, own) is expected


def test_canonical_types_contains_no_duplicates() -> None:
    """Список канонических типов без повторов и непустой."""
    assert len(CANONICAL_TYPES) == len(set(CANONICAL_TYPES))
    assert all(CANONICAL_TYPES)
