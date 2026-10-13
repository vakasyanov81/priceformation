"""Независимый классификатор типа товара: кейсы README.md, «Определение типа товара»."""

from __future__ import annotations

import pytest

from domain.row_item.row_item import RowItem
from parsers.strategies import product_types as pt
from parsers.strategies.product_type import ProductTypeClassifier

CAMERA = pt.CAMERA
DISK = pt.DISK
LIGHT_TRUCK = pt.LIGHT_TRUCK
MOTO = pt.MOTO
O_RING = pt.O_RING
PASSENGER = pt.PASSENGER
RIM_TAPE = pt.RIM_TAPE
SPECIAL = pt.SPECIAL
TRUCK = pt.TRUCK


@pytest.mark.parametrize(
    ('title', 'expected'),
    [
        ('Автокамера 11.2-20', CAMERA),
        ('Автокамера 12.5/80-18', CAMERA),
        ('Камера СВК 11.00-20 ГК-145', CAMERA),
        ('(Не использовать) Камера СВК 18.4-26 ТК', CAMERA),
        ('Ободная лента 16/70-20 (300-508)', RIM_TAPE),
        ('130-10 об/лента', RIM_TAPE),
        ('205-457 (12.00-18) об/лента', RIM_TAPE),
        ('Уплотнительное кольцо R25 d=6.6мм', O_RING),
        ('Уплотнительное кольцо R25 d=9.8мм', O_RING),
        ('5,5x16/6x170 ET106 D130 Газель Silver', DISK),
        ('7,5x22,5/10x335 ET165 D281 M22 Sil', DISK),
        ('17 TREBL 7.0*17 5*112 ЕТ43 57.1 Black', DISK),
        ('Диск стальной YONGZHENG 22,5*11,75 10 26мм ЕТ0 D281', DISK),
    ],
)
def test_non_tire_and_disk(title: str, expected: str) -> None:
    """Нешинные позиции и диски (README §3)."""
    assert ProductTypeClassifier().classify(RowItem({'title': title})) == expected


@pytest.mark.parametrize(
    ('title', 'expected'),
    [
        ('11.2-20 Ф-35 н.с.8 инд.114 НКШЗ сельхозшина', SPECIAL),
        ('16.9-28 Rockbuster H658 R-4', SPECIAL),
        ('17.5-25 RockBuster H108A E3/L3 н.с.28 спецшина', SPECIAL),
        ('17.5-25 Rockbuster H108A Е3/L3 28PR TL (волна бескамерная)', SPECIAL),
        ('23.1-26 Rockbuster H178А 16PR TT (ромбик камерная)', SPECIAL),
        ('10-16.5 RockBuster SKS-1 12PR TL (клюшка)', SPECIAL),
        ('18*7-8 (180/70-8) Haulking S-301 цельнолит. спецшина', SPECIAL),
        ('11.2-20 Ф-35 114A6', SPECIAL),
        ('14.9R30', SPECIAL),
        ('15.50R38', SPECIAL),
        ('520/70 R38 169A8', SPECIAL),
        ('6.50-10', SPECIAL),
        ('5.00-8', SPECIAL),
        ('9.00-20', SPECIAL),
        ('23.5R25', SPECIAL),
        ('17.5L-24', SPECIAL),
        ('28LR26 NORTEC H-23', SPECIAL),
        ('12.4L-16 Бел-160М 8PR', SPECIAL),
        ('30.5L-32 Nortec H-04 16PR 169A8 TT', SPECIAL),
        ('12.5/80-18 RockBuster H108D 16PR TL', SPECIAL),
        ('16/70-20 (300-508)', SPECIAL),
    ],
)
def test_special(title: str, expected: str) -> None:
    """Спецшины: маркеры, TRA, агро/индустриальные размеры (README §5.1)."""
    assert ProductTypeClassifier().classify(RowItem({'title': title})) == expected


@pytest.mark.parametrize(
    ('title', 'expected'),
    [
        ('315/80R22.5 Blackhawk BDR75 152/149M 18PR', TRUCK),
        ('10.00 R20 И-281 146/143J НКШЗ', TRUCK),
        ('7.50 R16 HIFLY HH-306 118/114M унив.ось', TRUCK),
        ('12.00R24 DRC D931 20PR', TRUCK),
        ('11.00-20', TRUCK),
        ('12.00-18 К-70 ОШЗ', TRUCK),
        ('11R22.5 TAITONG руль.ось', TRUCK),
        ('215/75R17.5', TRUCK),
        ('295/80R22.5', TRUCK),
        ('8.25R20', TRUCK),
        ('9.5R17.5', TRUCK),
        ('7.50R16', TRUCK),
    ],
)
def test_truck(title: str, expected: str) -> None:
    """Грузовые шины по диаметру, PR, двойному индексу и оси (README §5.3)."""
    assert ProductTypeClassifier().classify(RowItem({'title': title})) == expected


@pytest.mark.parametrize(
    ('title', 'expected'),
    [
        ('195/75R16C', LIGHT_TRUCK),
        ('285/75R16LT', LIGHT_TRUCK),
        ('165R13C', LIGHT_TRUCK),
        ('225/75R16C Triangle TV701 121/120S', LIGHT_TRUCK),
        ('7.00R16LT Triangle TR558', LIGHT_TRUCK),
        ('195/75 R16C VIATTI Vettore Brina (V-525) 107/105R', LIGHT_TRUCK),
        ('165 R13C Rapid EffiVan 94/93R', LIGHT_TRUCK),
        ('185 R14C Rapid EffiVan', LIGHT_TRUCK),
        ('225/75 R16 C', LIGHT_TRUCK),
        ('285/75 R16LT Rapid Mud', LIGHT_TRUCK),
        ('225/75R16 Sailun RXQuest Van TL', LIGHT_TRUCK),
        ('225/75R16 EffiVan TL', LIGHT_TRUCK),
        ('225/75R16 Tracvan TL', LIGHT_TRUCK),
        ('225/75R16 Connex Van TL', LIGHT_TRUCK),
        ('225/75R16 LCV TL', LIGHT_TRUCK),
        ('225/75R16 Cargo TL', LIGHT_TRUCK),
    ],
)
def test_light_truck(title: str, expected: str) -> None:
    """Легкогрузовые: суффиксы C/LT/CP и коммерческие модели (README §5.4)."""
    assert ProductTypeClassifier().classify(RowItem({'title': title})) == expected


@pytest.mark.parametrize(
    'title',
    [
        '225/70R15 Triangle AdvanteX SUV TR259 TL M+S 100H',
        '225/55R18 Sailun RXQuest SU01 TL 102W',
        '235/65R17 Sailun RXQuest H/T02 TL 104H',
    ],
)
def test_commercial_words_do_not_match_inside_other_words(title: str) -> None:
    """`van`/`rxquest` внутри слов (`AdvanteX`, SUV-линейка `RXQuest SU01`) — не коммерция.

    `AdvanteX` содержит `van`, а `RXQuest SU01` — SUV-линейка: оба легковые,
    а не легкогрузовые (границы слова в `_is_commercial`).
    """
    assert ProductTypeClassifier().classify(RowItem({'title': title})) == PASSENGER


@pytest.mark.parametrize(
    ('title', 'expected'),
    [
        ('205/55 R16 Rapid P309 91V', PASSENGER),
        ('235/55R17 Nordman 8 SUV 103T', PASSENGER),
        ('265/70R16', PASSENGER),
        ('215/65 R16 Кама НК-242 102T', PASSENGER),
        ('265/50R20 111V', PASSENGER),
        ('175/70 R13 КАМА ALGA НК-531', PASSENGER),
        ('165 R13', PASSENGER),
        ('245/45ZR18 Tracmax X-Privilo TX3 TL 100Y', PASSENGER),
    ],
)
def test_passenger(title: str, expected: str) -> None:
    """Легковые: метрический размер с одноместным индексом (README §5.5)."""
    assert ProductTypeClassifier().classify(RowItem({'title': title})) == expected


@pytest.mark.parametrize(
    ('title', 'expected'),
    [
        ('120/70-12', MOTO),
        ('130/80-17', MOTO),
        ('Мотошина 3.50-10', MOTO),
        ('Мото покрышка 110/90-17', MOTO),
    ],
)
def test_moto(title: str, expected: str) -> None:
    """Мотошины: маркеры мото или малый метрический размер (README §5.2)."""
    assert ProductTypeClassifier().classify(RowItem({'title': title})) == expected


@pytest.mark.parametrize(
    'title',
    [None, '', 'Nortec без размера', 'Шипы колёсные', 'Болты крепёжные'],
)
def test_undefined_type_is_empty(title: str | None) -> None:
    """Без размера и признаков тип не определён — пустая строка."""
    assert ProductTypeClassifier().classify(RowItem({'title': title})) == ''


def test_structured_fields_used_when_title_has_no_size() -> None:
    """Разобранные поля используются, если в названии формы нет."""
    row = RowItem({'title': 'Nortec грузовая', 'width': '315', 'height_percent': '80', 'diameter': '22.5'})

    assert ProductTypeClassifier().classify(row) == TRUCK
