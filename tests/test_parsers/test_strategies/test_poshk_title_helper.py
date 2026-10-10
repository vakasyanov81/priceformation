"""Разбор и сборка названия номенклатуры Пошка."""

import pytest

from domain.row_item.row_item import RowItem
from parsers.strategies._poshk_title_helper import (
    fill_poshk_fields,
    parse_poshk_title,
)

# Примеры склейки Пошк → Пионер (порядок: размер бренд модель нагрузка/скорость PR камера назначение).
_GLUE_EXAMPLES = (
    (
        '10.00 R20 DOUBLEROAD DR-801 н.с.18 149/146K унив.ось с об/л автошина, шт',
        '10.00R20 DOUBLEROAD DR-801 149/146K 18PR унив.ось с об/л',
    ),
    (
        '11 R22.5 TAITONG HS103 н.с.16 146/143M вед.ось автопокрышка, (1 шт)',
        '11R22.5 TAITONG HS103 146/143M 16PR вед.ось',
    ),
    (
        'а/п 425/85R21 NORTEC TR-184-1 18PR 156J TT, шт',
        '425/85R21 NORTEC TR-184-1 156J 18PR TT',
    ),
    (
        '11.00 R20 И-68А н.с. 16 150/146K НКШЗ автошина, шт',
        '11.00R20 НКШЗ И-68А 150/146K 16PR',
    ),
    (
        '12.4L-16 Бел-160М н.с.8 111A6 БШК сельхозшина, шт',
        '12.4L-16 БШК Бел-160М 111A6 8PR сельхозшина',
    ),
    (
        '17.5-25 Rockbuster H108A E3/L3 н.с.28 спецшина, шт',
        '17.5-25 Rockbuster H108A E3/L3 28PR спецшина',
    ),
)


@pytest.mark.parametrize(('raw', 'expected'), _GLUE_EXAMPLES)
def test_parse_and_compose_examples(raw: str, expected: str) -> None:
    """Склейка примера даёт порядок Пионера."""
    parts = parse_poshk_title(raw)

    assert parts is not None
    assert parts.compose() == expected


@pytest.mark.parametrize(('raw', 'expected'), _GLUE_EXAMPLES)
def test_compose_uses_brand_over_parsed(raw: str, expected: str) -> None:
    """Канонический бренд из поля перекрывает разобранный токен."""
    parts = parse_poshk_title(raw)

    assert parts is not None
    assert parts.compose('Brand') == expected.replace(parts.brand, 'Brand', 1)


def test_parse_splits_size_and_parameters() -> None:
    """Размер и параметры разобраны по отдельным полям."""
    parts = parse_poshk_title('10.00 R20 DOUBLEROAD DR-801 н.с.18 149/146K унив.ось с об/л автошина, шт')

    assert parts is not None
    assert parts.size.label == '10.00R20'
    assert parts.size.width == '10.00'
    assert parts.size.height_percent == ''
    assert parts.size.diameter == '20'
    assert (parts.brand, parts.model) == ('DOUBLEROAD', 'DR-801')
    assert (parts.load, parts.velocity) == ('149/146', 'K')
    assert (parts.layering, parts.intimacy) == ('18PR', '')
    assert parts.usage == ('унив.ось', 'с', 'об/л')


def test_parse_makes_producer_the_brand() -> None:
    """Производитель из хвоста становится брендом, если бренда в начале нет."""
    parts = parse_poshk_title('11.00 R20 И-68А н.с. 16 150/146K НКШЗ автошина, шт')

    assert parts is not None
    assert parts.brand == 'НКШЗ'
    assert parts.model == 'И-68А'
    assert parts.usage == ()


def test_parse_joins_split_size_and_low_marker() -> None:
    """Маркер низкого профиля ``L`` сохраняется, ``, шт`` срезается."""
    parts = parse_poshk_title('12.4L-16 Бел-160М н.с.8 111A6 БШК сельхозшина, шт')

    assert parts is not None
    assert parts.size.label == '12.4L-16'
    assert parts.size.width == '12.4'
    assert parts.brand == 'БШК'
    assert parts.model == 'Бел-160М'
    assert parts.layering == '8PR'
    assert parts.load == '111'
    assert parts.velocity == 'A6'


def test_parse_brand_keeps_producer_in_tail() -> None:
    """Латинский бренд/«Кама» в начале перекрывает производителя, тот едет в хвост."""
    tyrex = parse_poshk_title('11.00 R20 Tyrex CRG VM-310 н.с.16 150/146K ОШЗ автошина, (1 шт)')
    kama = parse_poshk_title('10.00 R20 КАМА-310 146/143K 16PR НКШЗ автошина, шт')

    assert tyrex is not None
    assert (tyrex.brand, tyrex.model) == ('Tyrex', 'CRG VM-310')
    assert tyrex.usage == ('ОШЗ',)
    assert kama is not None
    assert (kama.brand, kama.model) == ('КАМА-310', '')
    assert kama.usage == ('НКШЗ',)


def test_parse_joins_split_pr_and_strips_kind_suffix() -> None:
    """Разорванный ``8 PR`` склеивается, суффикс ``*автопокрышка`` срезается."""
    split_pr = parse_poshk_title('185/75 R16C THREE-A TRACVAN IMP 104/102R 8 PR б/к автопокрышка, шт')
    suffix = parse_poshk_title('185/75 R16С Sonix Winter X Pro Studs 77 104/102R шип.автопокрышка, шт')

    assert split_pr is not None
    assert split_pr.layering == '8PR'
    assert split_pr.usage == ('б/к',)
    assert suffix is not None
    assert suffix.usage == ('шип.',)


def test_parse_returns_none_for_disk() -> None:
    """Диск — не размер шины: разбор не срабатывает."""
    assert parse_poshk_title('Диск штамп NORTEC-16 11.75*22.5 10*335 ET0 d281 , шт') is None


def test_parse_returns_none_for_dual_size_tail() -> None:
    """Сдвоенная запись размера (``165-13/6.45-13``) не разбирается."""
    assert parse_poshk_title('Шина 165-13/6.45-13 АИ-168У 6PR 78P TT, шт') is None


def test_parse_returns_none_without_brand_model() -> None:
    """Только размер и служебные токены — модели нет, разбор пуст."""
    assert parse_poshk_title('Автошина 11R22.5 16PR 146/143L') is None


def test_parse_returns_none_for_producer_without_model() -> None:
    """Один производитель без бренда с моделью — разбор пуст."""
    assert parse_poshk_title('Автошина 12.00R20 16PR 150/146K НКШЗ') is None


def test_fill_poshk_fields_sets_parameters() -> None:
    """Разобранные параметры попадают в поля позиции."""
    row = RowItem({'title': '10.00 R20 DOUBLEROAD DR-801 н.с.18 149/146K унив.ось с об/л автошина, шт'})
    parts = parse_poshk_title(row.identity.title or '')

    assert parts is not None
    fill_poshk_fields(row, parts)

    assert row.tire.width == '10.00'
    assert row.tire.height_percent is None
    assert row.tire.diameter == '20'
    assert row.tire.layering == '18PR'
    assert row.tire.index_load == '149/146'
    assert row.tire.index_velocity == 'K'
    assert row.identity.model == 'DR-801'


def test_fill_poshk_fields_keeps_existing_values() -> None:
    """Уже заполненные поля разбор не перетирает."""
    row = RowItem(
        {
            'title': '10.00 R20 DOUBLEROAD DR-801 н.с.18 149/146K унив.ось с об/л автошина, шт',
            'width': '999',
            'model': 'Old',
        },
    )
    parts = parse_poshk_title(row.identity.title or '')

    assert parts is not None
    fill_poshk_fields(row, parts)

    assert row.tire.width == '999'
    assert row.identity.model == 'Old'
