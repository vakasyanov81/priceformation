"""Сравнение схем прайса: понятные русские описания расхождений."""

from openpyxl.utils import get_column_letter

from parsers.price_schema_models import Columns, PriceSchema, SheetSchema


def compare_schemas(old: PriceSchema, new: PriceSchema, columns: Columns) -> list[str]:
    """Описать расхождения схем по-русски; пусто — схема не изменилась."""
    lost_keys = sorted(old.json_keys - new.json_keys)
    changes = [_key_change(key, columns) for key in lost_keys]
    for index, old_sheet in old.sheets.items():
        new_sheet = new.sheets.get(index)
        if new_sheet is None:
            changes.append(_sheet_lost(index + 1, old_sheet.name))
        else:
            changes.extend(_sheet_changes(index, old_sheet, new_sheet, columns))
    return changes


def _sheet_changes(index: int, old: SheetSchema, new: SheetSchema, columns: Columns) -> list[str]:
    """Переименование вкладки и смена заголовков её колонок."""
    changes: list[str] = []
    if new.name != old.name:
        changes.append(_sheet_renamed(index + 1, old.name, new.name))
    for column in sorted(old.headers.keys() | new.headers.keys()):
        change = _header_change(old.headers.get(column), new.headers.get(column))
        if change:
            place = f'вкладка «{new.name}», колонка {get_column_letter(column + 1)}'
            changes.append(f'{place}: {change}{_usage(column, columns)}')
    return changes


def _header_change(before: str | None, after: str | None) -> str:
    """Что случилось с заголовком колонки; пусто — ничего."""
    if before == after:
        return ''
    if before is None:
        return f'появился заголовок «{after}»'
    if after is None:
        return f'пропал заголовок «{before}»'
    return f'заголовок «{before}» → «{after}»'


def _usage(column: int | str, columns: Columns) -> str:
    """Пояснение, в какое поле разбирается колонка."""
    return f' (используется как «{columns[column]}»)' if column in columns else ''


def _key_change(key: str, columns: Columns) -> str:
    """Сообщение о пропавшем поле json."""
    return f'в данных больше нет поля «{key}»{_usage(key, columns)}'


def _sheet_lost(number: int, name: str) -> str:
    return f'вкладка №{number} «{name}» пропала из файла'


def _sheet_renamed(number: int, before: str, after: str) -> str:
    return f'вкладка №{number} переименована: «{before}» → «{after}»'
