"""JSON-режим CLI."""

import json
from unittest.mock import MagicMock, create_autospec, patch

import pytest

from core.log_message import print_log
from parsers.common_price_output import jsonl_output_files
from parsers.row_item.row_item import RowItem
from run_argv import DOUBLES, GET_SUPLIERS, LOAD_CONFIG, LOAD_SUPPLIER_PRICES, PARSE, ZAPASKA_LOAD_API_DATA
from run_machine import fail_unknown_result_template, machine_json
from services.doubles_service import DoublesService
from services.parse_orchestrator import ParseOrchestrator
from services.price_report import PriceReportService
from services.zapaska_service import ZapaskaService

_TITLE = 'шина'
_PATH = 'file_prices/result/price.jsonl'
_DOUBLE_PATH = 'file_prices/result/doubles.jsonl'
_PRICE_FIELDS = {'title': _TITLE, 'price_opt': 10, 'price_markup': 12}
_RESOLVE = 'run_machine.ServiceProvider.resolve'
_LOG_NOISE = 'NOISE-ON-STDOUT'


def _assert_elapsed(payload: dict[str, object]) -> None:
    elapsed = payload.pop('elapsed_seconds')
    assert isinstance(elapsed, int | float)
    assert elapsed >= 0


def _result_with_row() -> MagicMock:
    row = RowItem(_PRICE_FIELDS)
    common = MagicMock()
    common.parsed_items = [row]
    common.unknown_category_skips = []
    common.black_list_skips = 0
    return common


def _mark_result(rows: list[RowItem]) -> MagicMock:
    common = MagicMock()
    common.parsed_items = rows
    common.unknown_category_skips = []
    common.black_list_skips = 0
    return common


def test_json_parse_success(capsys: pytest.CaptureFixture[str]) -> None:
    """parse --json без --all-parsed: статистика процесса, без позиций."""
    parsed = _result_with_row()
    orchestrator = MagicMock()
    orchestrator.parse_all.return_value = parsed
    reporter = MagicMock()
    reporter.write_prices.return_value = [_PATH]
    with patch(
        _RESOLVE,
        side_effect={ParseOrchestrator: orchestrator, PriceReportService: reporter}.__getitem__,
    ):
        code = machine_json(PARSE)
    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    _assert_elapsed(payload)
    assert payload['ok'] is True
    assert payload['action'] == PARSE
    assert payload['positions'] == []
    assert payload['stats']['items'] == 1
    assert payload['files'] == [_PATH]
    reporter.write_prices.assert_called_once_with(parsed.parsed_items, template=None, as_jsonl=True)


def test_json_parse_result_template(capsys: pytest.CaptureFixture[str]) -> None:
    """parse --parsed-template передаёт имя в write_prices."""
    parsed = _result_with_row()
    orchestrator = MagicMock()
    orchestrator.parse_all.return_value = parsed
    reporter = MagicMock()
    reporter.write_prices.return_value = [_PATH]
    with patch(
        _RESOLVE,
        side_effect={ParseOrchestrator: orchestrator, PriceReportService: reporter}.__getitem__,
    ):
        code = machine_json(PARSE, result_template='for_drom')
    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    _assert_elapsed(payload)
    reporter.write_prices.assert_called_once_with(parsed.parsed_items, template='for_drom', as_jsonl=True)


def test_json_parse_write_prices_keyword_only(capsys: pytest.CaptureFixture[str]) -> None:
    """write_prices принимает template только keyword-only (регрессия TypeError)."""
    parsed = _result_with_row()
    orchestrator = MagicMock()
    orchestrator.parse_all.return_value = parsed
    reporter = create_autospec(PriceReportService)
    reporter.write_prices.return_value = [_PATH]
    with patch(
        _RESOLVE,
        side_effect={ParseOrchestrator: orchestrator, PriceReportService: reporter}.__getitem__,
    ):
        code = machine_json(PARSE, result_template='for_drom')
    assert code == 0
    reporter.write_prices.assert_called_once_with(parsed.parsed_items, template='for_drom', as_jsonl=True)


def test_json_stdout_is_only_json(capsys: pytest.CaptureFixture[str]) -> None:
    """логи разбора не попадают в stdout и stderr."""
    parsed = _result_with_row()

    def noisy_parse_all() -> MagicMock:
        print_log(_LOG_NOISE)
        return parsed

    orchestrator = MagicMock()
    orchestrator.parse_all.side_effect = noisy_parse_all
    reporter = MagicMock()
    reporter.write_prices.return_value = [_PATH]
    with patch(
        _RESOLVE,
        side_effect={ParseOrchestrator: orchestrator, PriceReportService: reporter}.__getitem__,
    ):
        machine_json(PARSE)
    captured = capsys.readouterr()
    assert _LOG_NOISE not in captured.out
    assert _LOG_NOISE not in captured.err
    json.loads(captured.out)


def test_json_parse_all_result(capsys: pytest.CaptureFixture[str]) -> None:
    """parse --all-parsed: позиции в JSON."""
    parsed = _result_with_row()
    orchestrator = MagicMock()
    orchestrator.parse_all.return_value = parsed
    reporter = MagicMock()
    reporter.write_prices.return_value = [_PATH]
    with patch(
        _RESOLVE,
        side_effect={ParseOrchestrator: orchestrator, PriceReportService: reporter}.__getitem__,
    ):
        code = machine_json(PARSE, all_result=True)
    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    _assert_elapsed(payload)
    assert payload['positions'][0]['title'] == _TITLE
    assert payload['stats']['items'] == 1


def test_json_parse_error(capsys: pytest.CaptureFixture[str]) -> None:
    """исключение разбора → JSON с ok=false и код 1."""
    orchestrator = MagicMock()
    orchestrator.parse_all.side_effect = RuntimeError('boom')
    with patch(
        _RESOLVE,
        side_effect={ParseOrchestrator: orchestrator, PriceReportService: MagicMock()}.__getitem__,
    ):
        code = machine_json(PARSE)
    payload = json.loads(capsys.readouterr().out)
    assert code == 1
    _assert_elapsed(payload)
    assert payload['ok'] is False
    assert payload['error']['kind'] == 'RuntimeError'
    assert payload['error']['message'] == 'boom'


def test_json_keyboard_interrupt(capsys: pytest.CaptureFixture[str]) -> None:
    """KeyboardInterrupt → JSON-ошибка, код 1."""
    orchestrator = MagicMock()
    orchestrator.parse_all.side_effect = KeyboardInterrupt
    with patch(
        _RESOLVE,
        side_effect={ParseOrchestrator: orchestrator, PriceReportService: MagicMock()}.__getitem__,
    ):
        code = machine_json(PARSE)
    payload = json.loads(capsys.readouterr().out)
    assert code == 1
    _assert_elapsed(payload)
    assert payload['error']['kind'] == 'KeyboardInterrupt'


def test_json_doubles(capsys: pytest.CaptureFixture[str]) -> None:
    """doubles --json без --all-parsed: статистика, без позиций."""
    double_row = RowItem({'title': 'dup', 'price_opt': 1, 'price_markup': 2})
    double_row.is_double = True
    unique = RowItem({'title': 'uniq', 'price_opt': 1, 'price_markup': 2})
    parsed = _mark_result([double_row, unique])
    doubles_service = MagicMock()
    doubles_service.make_report.return_value = MagicMock(
        parse_result=parsed,
        doubles=[double_row],
        path=_DOUBLE_PATH,
    )
    with patch(_RESOLVE, side_effect={DoublesService: doubles_service}.__getitem__):
        code = machine_json(DOUBLES)
    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    _assert_elapsed(payload)
    assert payload['action'] == DOUBLES
    assert payload['positions'] == []
    assert payload['stats']['doubles'] == 1
    assert payload['files'] == jsonl_output_files([_DOUBLE_PATH])
    doubles_service.make_report.assert_called_once_with(as_jsonl=True)


def test_json_doubles_all_result(capsys: pytest.CaptureFixture[str]) -> None:
    """doubles --all-parsed отдаёт только дубли."""
    double_row = RowItem({'title': 'dup', 'price_opt': 1, 'price_markup': 2})
    double_row.is_double = True
    candidate = RowItem({'title': 'cand', 'price_opt': 1, 'price_markup': 2})
    candidate.double_candidate = True
    unique = RowItem({'title': 'uniq', 'price_opt': 1, 'price_markup': 2})
    parsed = _mark_result([double_row, candidate, unique])
    doubles_service = MagicMock()
    doubles_service.make_report.return_value = MagicMock(
        parse_result=parsed,
        doubles=[double_row, candidate],
        path=_DOUBLE_PATH,
    )
    with patch(_RESOLVE, side_effect={DoublesService: doubles_service}.__getitem__):
        code = machine_json(DOUBLES, all_result=True)
    payload = json.loads(capsys.readouterr().out)
    titles = {position['title'] for position in payload['positions']}
    assert code == 0
    _assert_elapsed(payload)
    assert titles == {'dup', 'cand'}
    assert payload['files'] == jsonl_output_files([_DOUBLE_PATH])


def test_json_unknown_command(capsys: pytest.CaptureFixture[str]) -> None:
    """неизвестная команда → JSON-ошибка."""
    code = machine_json('nope')
    payload = json.loads(capsys.readouterr().out)
    assert code == 1
    _assert_elapsed(payload)
    assert payload['ok'] is False
    assert payload['error']['kind'] == 'KeyError'


def test_json_zapaska(capsys: pytest.CaptureFixture[str]) -> None:
    """zapaska_load_api_data: compact ok, без полей разбора."""
    zapaska_service = MagicMock()
    with patch(_RESOLVE, side_effect={ZapaskaService: zapaska_service}.__getitem__):
        code = machine_json(ZAPASKA_LOAD_API_DATA)
    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    _assert_elapsed(payload)
    assert payload == {
        'ok': True,
        'action': ZAPASKA_LOAD_API_DATA,
    }
    zapaska_service.upload_data.assert_called_once_with()


def test_json_zapaska_error(capsys: pytest.CaptureFixture[str]) -> None:
    """ошибка zapaska_load_api_data → compact JSON."""
    zapaska_service = MagicMock()
    zapaska_service.upload_data.side_effect = RuntimeError('no net')
    with patch(_RESOLVE, side_effect={ZapaskaService: zapaska_service}.__getitem__):
        code = machine_json(ZAPASKA_LOAD_API_DATA)
    payload = json.loads(capsys.readouterr().out)
    assert code == 1
    _assert_elapsed(payload)
    assert payload['ok'] is False
    assert payload['action'] == ZAPASKA_LOAD_API_DATA
    assert payload['error']['kind'] == 'RuntimeError'
    assert 'positions' not in payload
    assert 'stats' not in payload


def test_json_get_supliers(capsys: pytest.CaptureFixture[str]) -> None:
    """get_supliers: каталог код → folder и название."""
    catalog = {'1': {'sup_code': 'poshk', 'sup_title': 'Пошк'}}
    with patch('run_machine.all_vendor_supplier_catalog', return_value=catalog):
        code = machine_json(GET_SUPLIERS)
    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    assert 'elapsed_seconds' not in payload
    assert payload == catalog


def test_json_load_supplier_prices(capsys: pytest.CaptureFixture[str]) -> None:
    """load_supplier_prices: ok, files и suppliers."""
    files = ['file_prices/poshk/price.xls']
    catalog = {'1': {'sup_code': 'poshk', 'sup_title': 'Пошк'}}
    raw = '{"1": "/incoming/any.xls"}'
    with (
        patch('run_machine.parse_prices_json', return_value={'1': '/incoming/any.xls'}) as mock_parse,
        patch('run_machine.load_supplier_prices', return_value=files) as mock_load,
        patch('run_machine.all_vendor_supplier_catalog', return_value=catalog),
    ):
        code = machine_json(LOAD_SUPPLIER_PRICES, supplier_prices=raw)
    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    _assert_elapsed(payload)
    assert payload == {
        'ok': True,
        'action': LOAD_SUPPLIER_PRICES,
        'files': files,
        'suppliers': {'1': 'Пошк'},
    }
    mock_parse.assert_called_once_with(raw)
    mock_load.assert_called_once_with({'1': '/incoming/any.xls'})


def test_json_load_supplier_prices_by_sup_code(capsys: pytest.CaptureFixture[str]) -> None:
    """load_supplier_prices: ключ sup_code в suppliers."""
    files = ['file_prices/poshk/price.xls']
    catalog = {'1': {'sup_code': 'poshk', 'sup_title': 'Пошк'}}
    raw = '{"poshk": "/incoming/any.xls"}'
    mapping = {'poshk': '/incoming/any.xls'}
    with (
        patch('run_machine.parse_prices_json', return_value=mapping),
        patch('run_machine.load_supplier_prices', return_value=files),
        patch('run_machine.all_vendor_supplier_catalog', return_value=catalog),
    ):
        code = machine_json(LOAD_SUPPLIER_PRICES, supplier_prices=raw)
    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    _assert_elapsed(payload)
    assert payload == {
        'ok': True,
        'action': LOAD_SUPPLIER_PRICES,
        'files': files,
        'suppliers': {'poshk': 'Пошк'},
    }


def test_json_load_supplier_prices_bad_json(capsys: pytest.CaptureFixture[str]) -> None:
    """битый JSON загрузки → ok=false."""
    code = machine_json(LOAD_SUPPLIER_PRICES, supplier_prices='not-json')
    payload = json.loads(capsys.readouterr().out)
    assert code == 1
    _assert_elapsed(payload)
    assert payload['ok'] is False
    assert payload['action'] == LOAD_SUPPLIER_PRICES
    assert payload['error']['kind'] == 'SupplierPricesMappingError'
    assert 'positions' not in payload
    assert 'stats' not in payload


def test_json_load_config(capsys: pytest.CaptureFixture[str]) -> None:
    """load_config: ok и files."""
    dests = ['parse_config/vendor_list.json']
    raw = '/incoming/vendor_list.json'
    with patch('run_machine.load_config', return_value=dests) as mock_load:
        code = machine_json(LOAD_CONFIG, config_path=raw)
    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    _assert_elapsed(payload)
    assert payload == {
        'ok': True,
        'action': LOAD_CONFIG,
        'files': dests,
    }
    mock_load.assert_called_once_with(raw)


def test_json_load_config_folder(capsys: pytest.CaptureFixture[str]) -> None:
    """load_config папки: несколько путей в files."""
    dests = ['parse_config/black_list', 'parse_config/vendor_list.json']
    raw = '/incoming/settings'
    with patch('run_machine.load_config', return_value=dests) as mock_load:
        code = machine_json(LOAD_CONFIG, config_path=raw)
    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    _assert_elapsed(payload)
    assert payload['files'] == dests
    mock_load.assert_called_once_with(raw)


def test_json_load_config_error(capsys: pytest.CaptureFixture[str]) -> None:
    """ошибка load_config → compact JSON."""
    code = machine_json(LOAD_CONFIG, config_path='')
    payload = json.loads(capsys.readouterr().out)
    assert code == 1
    _assert_elapsed(payload)
    assert payload['ok'] is False
    assert payload['action'] == LOAD_CONFIG
    assert payload['error']['kind'] == 'ConfigFileNotFoundError'
    assert 'positions' not in payload
    assert 'stats' not in payload


def test_run_machine_json_load_config() -> None:
    """load_config без --json уходит в JSON-режим с путём."""
    raw = '/incoming/vendor_list.json'
    with (
        patch('run.sys.argv', ['run.py', f'load_config={raw}']),
        patch('run.init_cfg'),
        patch('run.machine_json', return_value=0) as mock_json,
        patch('run.sys.exit', side_effect=SystemExit(0)),
    ):
        from run import main

        with pytest.raises(SystemExit):
            main()

        mock_json.assert_called_once_with(
            'load_config',
            all_result=False,
            result_template=None,
            supplier_prices=None,
            config_path=raw,
        )


def test_fail_unknown_skips_empty_name() -> None:
    """без имени шаблона проверки нет."""
    assert fail_unknown_result_template(PARSE, None, json_mode=True) is None


def test_fail_unknown_skips_known_name() -> None:
    """известное имя не считается ошибкой."""
    assert fail_unknown_result_template(PARSE, 'for_drom', json_mode=True) is None


def test_fail_unknown_json(capsys: pytest.CaptureFixture[str]) -> None:
    """неизвестный шаблон в JSON — ok=false."""
    code = fail_unknown_result_template(PARSE, 'nope', json_mode=True)
    payload = json.loads(capsys.readouterr().out)
    assert code == 1
    _assert_elapsed(payload)
    assert payload['ok'] is False
    assert payload['error']['kind'] == 'UnknownWriterTemplateError'
    assert 'nope' in payload['error']['message']


def test_fail_unknown_human(capsys: pytest.CaptureFixture[str]) -> None:
    """неизвестный шаблон без JSON — текст ошибки."""
    code = fail_unknown_result_template(PARSE, 'nope', json_mode=False)
    assert code == 1
    assert 'nope' in capsys.readouterr().out
