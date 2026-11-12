"""tests for CommonPriceOut"""

from datetime import date
from pathlib import Path
from typing import cast
from unittest.mock import ANY, MagicMock, patch

import pytest

from domain.config_context import get_config_provider
from domain.exceptions import ConfigValidationError
from domain.product_groups import ProductGroup
from domain.row_item.row_item import RowItem
from infrastructure.config.fake_config_provider import FakeConfigProvider
from parsers.common_price.output import CommonPriceOut
from parsers.data_provider.doubles_settings import DOUBLES_CONFIG_FILE, DoublesSettings
from parsers.writer.jsonl_meta import RESULT_META_FILE
from parsers.writer.jsonl_writer import jsonl_output_files
from parsers.writer.templates.all_templates import UnknownWriterTemplateError
from parsers.writer.templates.group_output import GroupOutput, OutputMode, TemplateOutput
from parsers.writer.templates.iwrite_template import IWriteTemplate
from parsers.writer.templates.sheet_template import SheetTemplate
from parsers.writer.templates.tmpl.for_doubles import ForDoubles
from parsers.writer.templates.tmpl.for_drom import ForDrom
from parsers.writer.templates.tmpl.for_full import ForFull
from parsers.writer.templates.tmpl.for_inner import ForInner
from parsers.writer.xls_writer import XlsWriter
from parsers.writer.xlsxwriter_adapter import XlsxWriterAdapter

_TITLE = 'title'
_REPORT_PATH = 'file_prices/result/doubles.xlsx'


def _result_folder() -> str:
    return get_config_provider().result_folder()


def _assert_sheet_template(actual: IWriteTemplate, expected: type[IWriteTemplate]) -> None:
    assert isinstance(actual, SheetTemplate)
    original = expected()
    assert actual.columns() == original.columns()
    assert actual.colors() == original.colors()
    assert actual.get_columns_format() == original.get_columns_format()
    assert actual.get_sheet_name() == 'price'
    assert actual.get_file_name() == original.resolve_file_name(date.today().isoformat())
    assert not actual.exclude()


def test_nomenclature_title_correction() -> None:
    """корректирует title у каждой позиции"""
    row_old = RowItem({_TITLE: 'old'})
    row_keep = RowItem({_TITLE: 'keep'})
    out = CommonPriceOut(
        [row_old, row_keep],
        xls_writer=cast(type[XlsWriter], MagicMock),
        write_driver=cast(type[XlsxWriterAdapter], MagicMock),
        config_provider=get_config_provider(),
    )

    with patch(
        'parsers.common_price.output.get_nomenclature_corrected_title',
        side_effect=lambda title, _provider: f'fixed-{title}' if title == 'old' else title,
    ):
        out.nomenclature_title_correction()

    assert row_old.identity.title == 'fixed-old'
    assert row_keep.identity.title == 'keep'


def test_write_all_prices() -> None:
    """write_all_prices корректирует названия и пишет по шаблонам"""
    rows = [RowItem({_TITLE: 't1'})]
    writer_cls = MagicMock()
    driver_cls = MagicMock()
    writer_instance = MagicMock()
    writer_instance.get_result_path.return_value = 'file_prices/result/inner.xlsx'
    writer_cls.return_value = writer_instance
    driver_instance = MagicMock()
    driver_cls.return_value = driver_instance
    template = ForInner
    out = CommonPriceOut(
        rows,
        xls_writer=cast(type[XlsWriter], writer_cls),
        write_driver=cast(type[XlsxWriterAdapter], driver_cls),
        config_provider=get_config_provider(),
    )
    raw_rows = [{_TITLE: 't1'}]

    with (
        patch.object(out, 'nomenclature_title_correction') as mock_corr,
        patch.object(out, 'write_doubles_report', return_value=_REPORT_PATH),
        patch('parsers.common_price.output.all_writer_templates', return_value=[template]),
    ):
        written = out.write_all_prices()

    mock_corr.assert_called_once()
    driver_cls.assert_called_once_with()
    writer_cls.assert_called_once_with(
        driver_instance,
        raw_rows,
        ANY,
        result_folder=_result_folder(),
    )
    _assert_sheet_template(writer_cls.call_args.args[2], template)
    writer_instance.write.assert_called_once()
    assert written == ['file_prices/result/inner.xlsx', _REPORT_PATH]


def test_drom_gets_merged_warehouses_and_inner_keeps_own_rows() -> None:
    """Дром получает склады одной группы объединёнными, свой прайс — строки по каждому складу."""
    writer_cls = MagicMock()
    out = CommonPriceOut(
        [_warehouse_row('A', 5000, 3), _warehouse_row('A', 5000, 4)],
        xls_writer=cast(type[XlsWriter], writer_cls),
        write_driver=cast(type[XlsxWriterAdapter], MagicMock()),
        config_provider=get_config_provider(),
    )

    with (
        patch.object(out, 'nomenclature_title_correction'),
        patch.object(out, 'write_doubles_report', return_value=_REPORT_PATH),
        patch('parsers.common_price.output.all_writer_templates', return_value=[ForInner, ForDrom]),
    ):
        out.write_all_prices()

    inner_rows, drom_rows = (call.args[1] for call in writer_cls.call_args_list)
    assert len(inner_rows) == 2
    assert len(drom_rows) == 1
    assert drom_rows[0]['rest_count'] == 7


def _warehouse_row(code: str, price: float, rest: int) -> RowItem:
    return RowItem(
        {
            'code': code,
            'title': f'Шина {code}',
            'price_markup': price,
            'rest_count': rest,
            'warehouse_group': 'novosibirsk',
            'warehouse_name': 'Новосибирск',
        },
    )


def test_write_all_prices_jsonl(fake_config_provider: FakeConfigProvider) -> None:
    """CLI пишет реальные потоки и реестр v2, не создавая XLSX."""
    out = CommonPriceOut(
        [RowItem({_TITLE: 't1'})],
        xls_writer=MagicMock(),
        write_driver=MagicMock(),
        config_provider=fake_config_provider,
        doubles_settings=DoublesSettings(),
    )
    with patch.object(out, 'nomenclature_title_correction'):
        written = out.write_all_prices(as_jsonl=True, result_template='for_inner')
    assert len(written) == 3
    assert all(Path(path).exists() for path in written)
    assert Path(written[1]).read_text(encoding='utf-8') == ''


def test_write_all_prices_reloads_nomenclature() -> None:
    """второй write_all_prices в том же процессе видит новую карту номенклатуры"""
    row = RowItem({_TITLE: 'old'})
    out = CommonPriceOut(
        [row],
        xls_writer=cast(type[XlsWriter], MagicMock),
        write_driver=cast(type[XlsxWriterAdapter], MagicMock),
        config_provider=get_config_provider(),
    )

    with (
        patch(
            'parsers.base_parser.nomenclature_correction.load_file',
            side_effect=[{'old': 'A'}, {'old': 'B'}],
        ),
        patch('parsers.common_price.output.all_writer_templates', return_value=[]),
        patch.object(out, 'write_doubles_report', return_value=_REPORT_PATH),
    ):
        out.write_all_prices()
        assert row.identity.title == 'A'
        row.set_field('title', 'old')
        out.write_all_prices()
        assert row.identity.title == 'B'


def test_write_doubles_report() -> None:
    """write_doubles_report пишет только размеченные дубли шаблоном ForDoubles"""
    double_row = RowItem({_TITLE: 'dup'})
    double_row.set_field('is_double', True)
    candidate = RowItem({_TITLE: 'cand'})
    candidate.set_field('double_candidate', True)
    unique = RowItem({_TITLE: 'uniq'})
    rows = [double_row, candidate, unique]
    writer_cls = MagicMock()
    driver_cls = MagicMock()
    driver_instance = MagicMock()
    driver_cls.return_value = driver_instance
    writer_instance = MagicMock()
    writer_instance.get_result_path.return_value = _REPORT_PATH
    writer_cls.return_value = writer_instance
    out = CommonPriceOut(
        rows,
        xls_writer=cast(type[XlsWriter], writer_cls),
        write_driver=cast(type[XlsxWriterAdapter], driver_cls),
        config_provider=get_config_provider(),
    )
    raw_rows = [double_row.to_dict(), candidate.to_dict()]

    with patch.object(out, 'nomenclature_title_correction') as mock_corr:
        report_path = out.write_doubles_report()

    mock_corr.assert_not_called()
    driver_cls.assert_called_once_with()
    writer_cls.assert_called_once_with(
        driver_instance,
        raw_rows,
        ANY,
        result_folder=_result_folder(),
    )
    _assert_sheet_template(writer_cls.call_args.args[2], ForDoubles)
    writer_instance.write.assert_called_once()
    assert report_path == _REPORT_PATH


def test_write_doubles_report_jsonl() -> None:
    """as_jsonl для дублей идёт в jsonl."""
    double_row = RowItem({_TITLE: 'dup'})
    double_row.set_field('is_double', True)
    out = CommonPriceOut(
        [double_row],
        xls_writer=cast(type[XlsWriter], MagicMock),
        write_driver=cast(type[XlsxWriterAdapter], MagicMock),
        config_provider=get_config_provider(),
    )
    jsonl_path = 'file_prices/result/doubles.jsonl'

    with patch('parsers.common_price.output.write_plan_jsonl', return_value=[jsonl_path]) as mock_jsonl:
        report_path = out.write_doubles_report(as_jsonl=True)
    books = mock_jsonl.call_args.args[0]
    sheet = books[0].sheets[0]
    assert sheet.rows[0]['title'] == 'dup'
    assert mock_jsonl.call_args.args[1] == _result_folder()
    assert report_path == jsonl_path


def test_write_all_prices_single_template() -> None:
    """result_template пишет только выбранный шаблон."""
    writer_cls = MagicMock()
    driver_cls = MagicMock()
    writer_instance = MagicMock()
    writer_instance.get_result_path.return_value = 'file_prices/result/drom.xlsx'
    writer_cls.return_value = writer_instance
    driver_instance = MagicMock()
    driver_cls.return_value = driver_instance
    out = CommonPriceOut(
        [RowItem({_TITLE: 't1', 'rest_count': 1})],
        xls_writer=cast(type[XlsWriter], writer_cls),
        write_driver=cast(type[XlsxWriterAdapter], driver_cls),
        config_provider=get_config_provider(),
    )
    raw_rows = [{_TITLE: 't1', 'rest_count': 1}]

    with (
        patch.object(out, 'nomenclature_title_correction'),
        patch.object(out, 'write_doubles_report', return_value=_REPORT_PATH),
    ):
        written = out.write_all_prices(result_template='for_drom')

    writer_cls.assert_called_once_with(
        driver_instance,
        raw_rows,
        ANY,
        result_folder=_result_folder(),
    )
    _assert_sheet_template(writer_cls.call_args.args[2], ForDrom)
    assert written == ['file_prices/result/drom.xlsx', _REPORT_PATH]


def test_write_all_prices_full_template() -> None:
    """for_full пишется только при явном выборе."""
    writer_cls = MagicMock()
    driver_cls = MagicMock()
    writer_instance = MagicMock()
    writer_instance.get_result_path.return_value = 'file_prices/result/full.xlsx'
    writer_cls.return_value = writer_instance
    driver_instance = MagicMock()
    driver_cls.return_value = driver_instance
    out = CommonPriceOut(
        [RowItem({_TITLE: 't1'})],
        xls_writer=cast(type[XlsWriter], writer_cls),
        write_driver=cast(type[XlsxWriterAdapter], driver_cls),
        config_provider=get_config_provider(),
    )
    raw_rows = [{_TITLE: 't1'}]

    with (
        patch.object(out, 'nomenclature_title_correction'),
        patch.object(out, 'write_doubles_report', return_value=_REPORT_PATH),
    ):
        written = out.write_all_prices(result_template='for_full')

    writer_cls.assert_called_once_with(
        driver_instance,
        raw_rows,
        ANY,
        result_folder=_result_folder(),
    )
    _assert_sheet_template(writer_cls.call_args.args[2], ForFull)
    assert written == ['file_prices/result/full.xlsx', _REPORT_PATH]


def test_write_all_prices_unknown_template() -> None:
    """неизвестный шаблон — ошибка до записи."""
    writer_cls = MagicMock()
    out = CommonPriceOut(
        [],
        xls_writer=cast(type[XlsWriter], writer_cls),
        write_driver=cast(type[XlsxWriterAdapter], MagicMock),
        config_provider=get_config_provider(),
    )

    with pytest.raises(UnknownWriterTemplateError, match='nope'):
        out.write_all_prices(result_template='nope')

    writer_cls.assert_not_called()


def test_jsonl_output_files_appends_meta() -> None:
    """к jsonl добавляется result_meta.json из той же папки."""
    jsonl_path = 'file_prices/result/price.jsonl'
    assert jsonl_output_files([jsonl_path]) == [
        jsonl_path,
        str(Path(jsonl_path).parent / RESULT_META_FILE),
    ]


def test_jsonl_output_files_empty() -> None:
    """без jsonl мета не добавляется."""
    assert not jsonl_output_files([])


def test_jsonl_output_files_skips_duplicate_meta() -> None:
    """повторно мета не дописывается."""
    jsonl_path = 'file_prices/result/price.jsonl'
    once = jsonl_output_files([jsonl_path])
    assert jsonl_output_files(once) == once


def _double_row(supplier: str, price: float) -> RowItem:
    row_item = RowItem({'supplier_name': supplier, _TITLE: 'Шина', 'price_markup': price, 'rest_count': 2})
    row_item.set_field('group_by_params', 1)
    row_item.set_field('is_double', True)
    return row_item


def test_drom_excludes_doubles_by_settings_and_inner_keeps_them() -> None:
    """Дубли исключаются только в шаблоне из настроек; доклад о дублях пишется вместе с прайсами."""
    writer_cls = MagicMock()
    out = CommonPriceOut(
        [_double_row('Пошк', 5000), _double_row('Автоснабжение', 6000)],
        xls_writer=cast(type[XlsWriter], writer_cls),
        write_driver=cast(type[XlsxWriterAdapter], MagicMock()),
        config_provider=get_config_provider(),
        doubles_settings=DoublesSettings(exclude_in_templates=('for_drom',), priority_suppliers=('Автоснабжение',)),
    )

    with (
        patch.object(out, 'nomenclature_title_correction'),
        patch('parsers.common_price.output.all_writer_templates', return_value=[ForInner, ForDrom]),
    ):
        out.write_all_prices()

    (inner_rows, inner_tmpl), (drom_rows, drom_tmpl), (doubles_rows, doubles_tmpl) = (
        call.args[1:3] for call in writer_cls.call_args_list
    )
    _assert_sheet_template(inner_tmpl, ForInner)
    _assert_sheet_template(drom_tmpl, ForDrom)
    _assert_sheet_template(doubles_tmpl, ForDoubles)
    assert len(inner_rows) == 2
    assert [row['supplier_name'] for row in drom_rows] == ['Автоснабжение']
    assert len(doubles_rows) == 2


def test_doubles_report_puts_priority_supplier_first_within_group() -> None:
    """В отчёте о дублях приоритетный поставщик первый в своей группе, порядок остальных не меняется."""
    writer_cls = MagicMock()
    other_group = _double_row('Автоснабжение', 1)
    other_group.set_field('group_by_params', 2)
    out = CommonPriceOut(
        [_double_row('Пошк', 5000), _double_row('Мим', 4000), _double_row('Автоснабжение', 6000), other_group],
        xls_writer=cast(type[XlsWriter], writer_cls),
        write_driver=cast(type[XlsxWriterAdapter], MagicMock()),
        config_provider=get_config_provider(),
        doubles_settings=DoublesSettings(priority_suppliers=('Автоснабжение',)),
    )

    with patch.object(out, 'nomenclature_title_correction'):
        out.write_doubles_report()

    rows = writer_cls.call_args.args[1]
    assert [row['supplier_name'] for row in rows] == ['Автоснабжение', 'Пошк', 'Мим', 'Автоснабжение']


def test_doubles_report_puts_groups_with_priority_supplier_on_top() -> None:
    """Группа с приоритетным поставщиком идёт выше групп без него, даже если её номер больше."""
    writer_cls = MagicMock()
    plain = _double_row('Пошк', 5000)
    plain.set_field('group_by_params', 1)
    priority = _double_row('Автоснабжение', 6000)
    priority.set_field('group_by_params', 2)
    out = CommonPriceOut(
        [plain, _double_row('Мим', 4000), priority],
        xls_writer=cast(type[XlsWriter], writer_cls),
        write_driver=cast(type[XlsxWriterAdapter], MagicMock()),
        config_provider=get_config_provider(),
        doubles_settings=DoublesSettings(priority_suppliers=('Автоснабжение',)),
    )

    with patch.object(out, 'nomenclature_title_correction'):
        out.write_doubles_report()

    rows = writer_cls.call_args.args[1]
    assert rows[0]['supplier_name'] == 'Автоснабжение'


def test_doubles_settings_are_read_from_config(fake_config_provider: FakeConfigProvider) -> None:
    """Без переданных настроек читается parse_config/doubles.json."""
    path = Path(fake_config_provider.config_file(DOUBLES_CONFIG_FILE))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('{"exclude_in_templates": ["for_drom"]}', encoding='UTF-8')
    writer_cls = MagicMock()
    out = CommonPriceOut(
        [_double_row('Пошк', 5000), _double_row('Мим', 4000)],
        xls_writer=cast(type[XlsWriter], writer_cls),
        write_driver=cast(type[XlsxWriterAdapter], MagicMock()),
        config_provider=fake_config_provider,
    )

    with (
        patch.object(out, 'nomenclature_title_correction'),
        patch.object(out, 'write_doubles_report', return_value=_REPORT_PATH),
    ):
        out.write_all_prices(result_template='for_drom')

    drom_rows = writer_cls.call_args.args[1]
    assert [row['supplier_name'] for row in drom_rows] == ['Мим']


def test_result_folder_comes_from_injected_provider() -> None:
    """папка результата берётся у переданного провайдера, а не у глобального локатора"""
    injected = MagicMock()
    injected.result_folder.return_value = '/injected/result'
    out = CommonPriceOut(
        [RowItem({_TITLE: 'a'})],
        xls_writer=cast(type[XlsWriter], MagicMock()),
        write_driver=cast(type[XlsxWriterAdapter], MagicMock()),
        config_provider=injected,
        doubles_settings=DoublesSettings(),
    )

    with patch('parsers.common_price.output.write_plan_jsonl', return_value=['x.jsonl']) as write:
        out.write_doubles_report(as_jsonl=True)

    assert write.call_args.args[1] == '/injected/result'


@pytest.mark.parametrize('as_jsonl', [False, True])
def test_invalid_later_template_prevents_all_writes(as_jsonl: bool) -> None:
    """Ошибка второго шаблона не оставляет готовый файл первого."""
    writer = MagicMock()
    driver = MagicMock()
    out = CommonPriceOut([], xls_writer=writer, write_driver=driver, config_provider=get_config_provider())
    invalid = ForDrom().output_spec()
    invalid.groups[0].filters['foreign_field'] = []
    with (
        patch.object(ForDrom, 'output_spec', return_value=invalid),
        patch('parsers.common_price.output.write_plan_jsonl') as jsonl,
        pytest.raises(ConfigValidationError, match=r'for_drom.*filters'),
    ):
        out.write_all_prices(as_jsonl=as_jsonl)
    writer.assert_not_called()
    driver.assert_not_called()
    jsonl.assert_not_called()


def test_xlsx_uses_group_description_and_one_date(fake_config_provider: FakeConfigProvider) -> None:
    """План определяет реальные файл, лист, колонки и фильтры, а не старые атрибуты шаблона."""
    import openpyxl

    group = GroupOutput(
        ProductGroup.TIRE_AND_DISK,
        'Свой лист',
        [{'Своё название': {'field': 'title'}}],
        {'title': ['убрать']},
        {},
        file_name='custom_{now}.xlsx',
    )
    output = TemplateOutput('for_inner', OutputMode.SEPARATE_FILES, (group,))
    doubles_output = ForDoubles().output_spec()
    out = CommonPriceOut(
        [RowItem({'title': 'оставить'}), RowItem({'title': 'убрать'})],
        xls_writer=XlsWriter,
        write_driver=XlsxWriterAdapter,
        config_provider=fake_config_provider,
        doubles_settings=DoublesSettings(),
    )
    with (
        patch.object(ForInner, 'output_spec', return_value=output),
        patch.object(ForDoubles, 'output_spec', return_value=doubles_output),
        patch('parsers.common_price.output.all_writer_templates', return_value=[ForInner]),
        patch('parsers.common_price.output.date') as clock,
        patch.object(out, 'nomenclature_title_correction'),
    ):
        clock.today.return_value = date(2000, 1, 2)
        paths = out.write_all_prices()
    clock.today.assert_called_once_with()
    assert [Path(path).name for path in paths] == [
        'custom_2000-01-02.xlsx',
        ForDoubles().resolve_file_name('2000-01-02'),
    ]
    assert all(Path(path).is_file() for path in paths)
    book = openpyxl.load_workbook(paths[0])
    try:
        assert book.sheetnames == ['Свой лист']
        assert list(book['Свой лист'].values) == [('Своё название',), ('оставить',)]
    finally:
        book.close()
