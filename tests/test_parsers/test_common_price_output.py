"""tests for CommonPriceOut"""

from pathlib import Path
from typing import cast
from unittest.mock import MagicMock, patch

import pytest

from domain.config_context import get_config_provider
from domain.row_item.row_item import RowItem
from infrastructure.config.fake_config_provider import FakeConfigProvider
from parsers.common_price.output import CommonPriceOut, jsonl_output_files
from parsers.data_provider.doubles_settings import DOUBLES_CONFIG_FILE, DoublesSettings
from parsers.writer.jsonl_writer import RESULT_META_FILE
from parsers.writer.templates.all_templates import UnknownWriterTemplateError
from parsers.writer.templates.tmpl.for_doubles import ForDoubles
from parsers.writer.templates.tmpl.for_drom import ForDrom
from parsers.writer.templates.tmpl.for_full import ForFull
from parsers.writer.templates.tmpl.for_inner import ForInner
from parsers.writer.xls_writer import XlsWriter
from parsers.writer.xlsx_driver import XlsxWriterDriver

_TITLE = 'title'
_REPORT_PATH = 'file_prices/result/doubles.xlsx'


def _result_folder() -> str:
    return get_config_provider().result_folder()


def test_nomenclature_title_correction() -> None:
    """корректирует title у каждой позиции"""
    row_old = RowItem({_TITLE: 'old'})
    row_keep = RowItem({_TITLE: 'keep'})
    out = CommonPriceOut(
        [row_old, row_keep],
        xls_writer=cast(type[XlsWriter], MagicMock),
        write_driver=cast(type[XlsxWriterDriver], MagicMock),
    )

    with patch(
        'parsers.common_price.output.get_nomenclature_corrected_title',
        side_effect=lambda title: f'fixed-{title}' if title == 'old' else title,
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
        write_driver=cast(type[XlsxWriterDriver], driver_cls),
    )
    raw_rows = [{_TITLE: 't1'}]

    with (
        patch.object(out, 'nomenclature_title_correction') as mock_corr,
        patch.object(out, 'write_doubles_report', return_value=_REPORT_PATH),
        patch('parsers.common_price.output.all_writer_templates', return_value=[template]),
        patch(
            'parsers.common_price.output._to_raw_dicts',
            return_value=raw_rows,
        ) as mock_raw,
    ):
        written = out.write_all_prices()

    mock_corr.assert_called_once()
    mock_raw.assert_called_once_with(rows)
    driver_cls.assert_called_once_with()
    writer_cls.assert_called_once_with(
        driver_instance,
        raw_rows,
        template,
        result_folder=_result_folder(),
    )
    writer_instance.write.assert_called_once()
    assert written == ['file_prices/result/inner.xlsx', _REPORT_PATH]


def test_drom_gets_merged_warehouses_and_inner_keeps_own_rows() -> None:
    """Дром получает склады одной группы объединёнными, свой прайс — строки по каждому складу."""
    writer_cls = MagicMock()
    out = CommonPriceOut(
        [_warehouse_row('A', 5000, 3), _warehouse_row('A', 5000, 4)],
        xls_writer=cast(type[XlsWriter], writer_cls),
        write_driver=cast(type[XlsxWriterDriver], MagicMock()),
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


def test_write_all_prices_jsonl() -> None:
    """as_jsonl пишет jsonl и не трогает xlsx writer."""
    rows = [RowItem({_TITLE: 't1'})]
    writer_cls = MagicMock()
    driver_cls = MagicMock()
    template = ForInner
    out = CommonPriceOut(
        rows,
        xls_writer=cast(type[XlsWriter], writer_cls),
        write_driver=cast(type[XlsxWriterDriver], driver_cls),
    )
    raw_rows = [{_TITLE: 't1'}]
    jsonl_path = 'file_prices/result/price.jsonl'

    doubles_path = 'file_prices/result/doubles.jsonl'

    with (
        patch.object(out, 'nomenclature_title_correction') as mock_corr,
        patch.object(out, 'write_doubles_report', return_value=doubles_path) as mock_doubles,
        patch('parsers.common_price.output.all_writer_templates', return_value=[template]),
        patch('parsers.common_price.output._to_raw_dicts', return_value=raw_rows),
        patch('parsers.common_price.output.write_template_jsonl', return_value=jsonl_path) as mock_jsonl,
    ):
        written = out.write_all_prices(as_jsonl=True)

    mock_corr.assert_called_once()
    writer_cls.assert_not_called()
    mock_jsonl.assert_called_once_with(raw_rows, template, _result_folder())
    mock_doubles.assert_called_once_with(as_jsonl=True)
    assert written == jsonl_output_files([jsonl_path, doubles_path])


def test_write_all_prices_reloads_nomenclature() -> None:
    """второй write_all_prices в том же процессе видит новую карту номенклатуры"""
    row = RowItem({_TITLE: 'old'})
    out = CommonPriceOut(
        [row],
        xls_writer=cast(type[XlsWriter], MagicMock),
        write_driver=cast(type[XlsxWriterDriver], MagicMock),
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
        write_driver=cast(type[XlsxWriterDriver], driver_cls),
    )
    raw_rows = [{_TITLE: 'dup'}, {_TITLE: 'cand'}]

    with (
        patch.object(out, 'nomenclature_title_correction') as mock_corr,
        patch(
            'parsers.common_price.output._to_raw_dicts',
            return_value=raw_rows,
        ) as mock_raw,
    ):
        report_path = out.write_doubles_report()

    mock_corr.assert_not_called()
    mock_raw.assert_called_once_with([double_row, candidate])
    driver_cls.assert_called_once_with()
    writer_cls.assert_called_once_with(
        driver_instance,
        raw_rows,
        ForDoubles,
        result_folder=_result_folder(),
    )
    writer_instance.write.assert_called_once()
    assert report_path == _REPORT_PATH


def test_write_doubles_report_jsonl() -> None:
    """as_jsonl для дублей идёт в jsonl."""
    double_row = RowItem({_TITLE: 'dup'})
    double_row.set_field('is_double', True)
    out = CommonPriceOut(
        [double_row],
        xls_writer=cast(type[XlsWriter], MagicMock),
        write_driver=cast(type[XlsxWriterDriver], MagicMock),
    )
    jsonl_path = 'file_prices/result/doubles.jsonl'
    raw_rows = [{_TITLE: 'dup'}]

    with (
        patch('parsers.common_price.output._to_raw_dicts', return_value=raw_rows),
        patch('parsers.common_price.output.write_template_jsonl', return_value=jsonl_path) as mock_jsonl,
    ):
        report_path = out.write_doubles_report(as_jsonl=True)

    mock_jsonl.assert_called_once_with(raw_rows, ForDoubles, _result_folder())
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
        [RowItem({_TITLE: 't1'})],
        xls_writer=cast(type[XlsWriter], writer_cls),
        write_driver=cast(type[XlsxWriterDriver], driver_cls),
    )
    raw_rows = [{_TITLE: 't1'}]

    with (
        patch.object(out, 'nomenclature_title_correction'),
        patch.object(out, 'write_doubles_report', return_value=_REPORT_PATH),
        patch('parsers.common_price.output._to_raw_dicts', return_value=raw_rows),
    ):
        written = out.write_all_prices(result_template='for_drom')

    writer_cls.assert_called_once_with(
        driver_instance,
        raw_rows,
        ForDrom,
        result_folder=_result_folder(),
    )
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
        write_driver=cast(type[XlsxWriterDriver], driver_cls),
    )
    raw_rows = [{_TITLE: 't1'}]

    with (
        patch.object(out, 'nomenclature_title_correction'),
        patch.object(out, 'write_doubles_report', return_value=_REPORT_PATH),
        patch('parsers.common_price.output._to_raw_dicts', return_value=raw_rows),
    ):
        written = out.write_all_prices(result_template='for_full')

    writer_cls.assert_called_once_with(
        driver_instance,
        raw_rows,
        ForFull,
        result_folder=_result_folder(),
    )
    assert written == ['file_prices/result/full.xlsx', _REPORT_PATH]


def test_write_all_prices_unknown_template() -> None:
    """неизвестный шаблон — ошибка до записи."""
    writer_cls = MagicMock()
    out = CommonPriceOut(
        [],
        xls_writer=cast(type[XlsWriter], writer_cls),
        write_driver=cast(type[XlsxWriterDriver], MagicMock),
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
        write_driver=cast(type[XlsxWriterDriver], MagicMock()),
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
    assert (inner_tmpl, drom_tmpl, doubles_tmpl) == (ForInner, ForDrom, ForDoubles)
    assert len(inner_rows) == 2
    assert [row['supplier_name'] for row in drom_rows] == ['Автоснабжение']
    assert len(doubles_rows) == 2


def test_doubles_settings_are_read_from_config(fake_config_provider: FakeConfigProvider) -> None:
    """Без переданных настроек читается parse_config/doubles.json."""
    path = Path(fake_config_provider.config_file(DOUBLES_CONFIG_FILE))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('{"exclude_in_templates": ["for_drom"]}', encoding='UTF-8')
    writer_cls = MagicMock()
    out = CommonPriceOut(
        [_double_row('Пошк', 5000), _double_row('Мим', 4000)],
        xls_writer=cast(type[XlsWriter], writer_cls),
        write_driver=cast(type[XlsxWriterDriver], MagicMock()),
    )

    with (
        patch.object(out, 'nomenclature_title_correction'),
        patch.object(out, 'write_doubles_report', return_value=_REPORT_PATH),
    ):
        out.write_all_prices(result_template='for_drom')

    drom_rows = writer_cls.call_args.args[1]
    assert [row['supplier_name'] for row in drom_rows] == ['Мим']
