"""Независимые JSONL-потоки групп и реестр схем v2."""

import datetime
from pathlib import Path

from parsers.writer.jsonl_meta import RESULT_META_FILE, FileRegistry
from parsers.writer.jsonl_packing import PackedFile, pack_rows
from parsers.writer.jsonl_publish import publish_jsonl
from parsers.writer.output_paths import jsonl_name
from parsers.writer.output_plan import SheetPlan, WorkbookPlan
from parsers.writer.row_style import PriceRow
from parsers.writer.templates.iwrite_template import IWriteTemplate
from parsers.writer.xls_writer import make_exclude


def write_template_jsonl(rows: list[PriceRow], template: type[IWriteTemplate], result_folder: str) -> str:
    """Совместимый вход для одногрупповых шаблонов; метаданные всегда v2."""
    instance = template()
    group = instance.output_spec().groups[0]
    filtered = make_exclude(rows, group.filters)
    sheet = SheetPlan(group, tuple(filtered), frozenset(('title',)))
    book = WorkbookPlan(instance.template_id, _template_name(instance), (sheet,))
    return write_plan_jsonl((book,), result_folder)[0]


def write_plan_jsonl(books: tuple[WorkbookPlan, ...], result_folder: str) -> list[str]:
    """Записать по потоку на группу независимо от размещения листов XLSX."""
    packed = _pack_books(books)
    streams = {name: stream[0] for name, stream in packed.items()}
    schemas: FileRegistry = {name: stream[1] for name, stream in packed.items()}
    return publish_jsonl(Path(result_folder), streams, schemas)


def _pack_books(books: tuple[WorkbookPlan, ...]) -> dict[str, PackedFile]:
    packed = {}
    for book in books:
        for sheet in book.sheets:
            name = jsonl_name(book.file_name, book.mode, sheet.settings.id)
            packed[name] = _pack_sheet(book.template_id, sheet)
    return packed


def _pack_sheet(template_id: str, sheet: SheetPlan) -> PackedFile:
    rows = [dict(row) for row in sheet.rows]
    packed, schema = pack_rows(rows, sheet.settings.columns, sheet.title_fields)
    schema.update(
        template_id=template_id, product_group=sheet.settings.id, schema_version=sheet.settings.schema_version
    )
    return packed, schema


def _template_name(template: IWriteTemplate) -> str:
    name = template.get_file_name().format(now=datetime.date.today().isoformat())
    return Path(name).with_suffix('.jsonl').name


def jsonl_output_files(written: list[str]) -> list[str]:
    """Пути jsonl и файл метаинформации колонок в той же папке."""
    if not written:
        return written
    meta = str(Path(written[0]).parent / RESULT_META_FILE)
    if meta in written:
        return written
    return [*written, meta]
