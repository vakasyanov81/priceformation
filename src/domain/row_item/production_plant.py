"""Завод-изготовитель шины по названию позиции."""

import re

# Написание в прайсах → каноническое; ключи в нижнем регистре.
_PLANTS = {
    'нкшз': 'НкШЗ',
    'нк.шз': 'НкШЗ',
    'ошз': 'ОШЗ',
    'яшз': 'ЯШЗ',
    'волшз': 'ВолШЗ',
    'бшк': 'БШК',
}
_SPELLINGS = '|'.join(re.escape(spelling) for spelling in _PLANTS)
_PLANT_RE = re.compile(rf'(?<![\w.])({_SPELLINGS})(?!\w)', re.IGNORECASE)


def production_plant(title: str | None) -> str | None:
    """Завод из «НкШЗ», «ОШЗ», «ЯШЗ», «ВолШЗ», «БШК» (любой регистр); нет признака → None."""
    match = _PLANT_RE.search(title or '')
    return _PLANTS[match[1].lower()] if match else None
