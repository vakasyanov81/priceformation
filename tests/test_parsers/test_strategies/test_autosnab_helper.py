"""Разбор размера и модели из title Автоснабжения."""

import pytest

from domain.row_item.row_item import RowItem
from parsers.strategies._autosnab_helper import fill_from_title


@pytest.mark.parametrize(
    ('title', 'width', 'height', 'diameter'),
    [
        ('205/55R16', '205', '55', '16'),
        ('22,5/40R18', '22.5', '40', '18'),
        ('205/55,5R16', '205', '55.5', '16'),
        ('205/55R16,5', '205', '55', '16.5'),
    ],
)
def test_fill_from_title_profile_size(title: str, width: str, height: str, diameter: str) -> None:
    """Профильный размер: десятичные запятые канонизируются, внешний диаметр пуст."""
    row = RowItem({'title': title})

    fill_from_title(row)

    assert row.tire.width == width
    assert row.tire.height_percent == height
    assert row.tire.diameter == diameter
    assert row.tire.ext_diameter is None
    assert row.parse_errors == {}


def test_fill_from_title_flat_size() -> None:
    """Плоский размер без профиля: высота и внешний диаметр не заполняются."""
    row = RowItem({'title': '205R16'})

    fill_from_title(row)

    assert row.tire.width == '205'
    assert row.tire.height_percent is None
    assert row.tire.diameter == '16'
    assert row.tire.ext_diameter is None
    assert row.parse_errors == {}


def test_fill_from_title_flat_model_uses_rest_after_size() -> None:
    """Модель плоского размера берётся из хвоста после размера."""
    row = RowItem({'title': '205R16 Model'})

    fill_from_title(row)

    assert row.identity.model == 'Model'


def test_fill_from_title_inch_size() -> None:
    """Дюймовый размер заполняет внешний диаметр, профиль не заполняется."""
    row = RowItem({'title': '31x10.5R15'})

    fill_from_title(row)

    assert row.tire.ext_diameter == 31
    assert row.tire.width == '10.5'
    assert row.tire.diameter == '15'
    assert row.tire.height_percent is None


def test_fill_from_title_inch_model_uses_rest_after_size() -> None:
    """Модель дюймового размера берётся из хвоста после размера."""
    row = RowItem({'title': '31x10.5R15 Model'})

    fill_from_title(row)

    assert row.identity.model == 'Model'


def test_fill_from_title_keeps_existing_height() -> None:
    """Заполненный профиль не перезаписывается разобранным из title."""
    row = RowItem({'title': '205/55R16', 'height_percent': '60'})

    fill_from_title(row)

    assert row.tire.height_percent == '60'


def test_fill_from_title_keeps_existing_ext_diameter() -> None:
    """Заполненный внешний диаметр не перезаписывается."""
    row = RowItem({'title': '31x10.5R15', 'ext_diameter': '30'})

    fill_from_title(row)

    assert row.tire.ext_diameter == 30


def test_fill_from_title_model_from_manufacturer() -> None:
    """Производитель в начале остатка срезается перед разбором модели."""
    row = RowItem({'title': '205/55R16 Nokian Hakka', 'manufacturer_name': 'Nokian'})

    fill_from_title(row)

    assert row.identity.model == 'Hakka'


def test_fill_from_title_model_from_brand() -> None:
    """Бренд в начале остатка срезается перед разбором модели."""
    row = RowItem({'title': '205/55R16 Nokian Hakka', 'brand': 'Nokian'})

    fill_from_title(row)

    assert row.identity.model == 'Hakka'


def test_fill_from_title_keeps_existing_model() -> None:
    """Заполненная модель не перезаписывается разобранной из title."""
    row = RowItem({'title': '205/55R16 Model', 'model': 'Old'})

    fill_from_title(row)

    assert row.identity.model == 'Old'


def test_fill_from_title_model_drops_parentheses() -> None:
    """Скобочные пометки в остатке не попадают в модель."""
    row = RowItem({'title': '205/55R16 Model (RFT)'})

    fill_from_title(row)

    assert row.identity.model == 'Model'


def test_fill_from_title_model_multiword() -> None:
    """Модель из нескольких токенов склеивается пробелом."""
    row = RowItem({'title': '205/55R16 Model A B'})

    fill_from_title(row)

    assert row.identity.model == 'Model A B'


def test_fill_from_title_model_stops_at_service_token() -> None:
    """Служебный токен (PR) завершает модель."""
    row = RowItem({'title': '205/55R16 Model 16PR'})

    fill_from_title(row)

    assert row.identity.model == 'Model'


def test_fill_from_title_model_stops_at_stop_word() -> None:
    """Стоп-слово из набора (TL) завершает модель."""
    row = RowItem({'title': '205/55R16 Model TL'})

    fill_from_title(row)

    assert row.identity.model == 'Model'


def test_fill_from_title_model_stops_at_load_speed() -> None:
    """Индекс нагрузки/скорости завершает модель."""
    row = RowItem({'title': '205/55R16 Model 104R'})

    fill_from_title(row)

    assert row.identity.model == 'Model'


def test_fill_from_title_lstrip_placeholder_is_literal() -> None:
    """Без производителя/бренда литерал 'XXXX' не считается префиксом."""
    row = RowItem({'title': '205/55R16 XXXX Model'})

    fill_from_title(row)

    assert row.identity.model == 'XXXX Model'


def test_fill_from_title_no_match_untouched() -> None:
    """Без размера в начале title поля не трогаются."""
    row = RowItem({'title': 'не размер'})

    fill_from_title(row)

    assert row.tire.width is None
    assert row.tire.diameter is None
    assert row.identity.model is None
