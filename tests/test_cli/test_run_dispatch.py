"""Диспетчер неинтерактивных команд app.run.main."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from infrastructure.config.fake_config_provider import FakeConfigProvider


def test_run_machine_json_dispatch() -> None:
    """parse --json уходит в machine_json и завершает процесс его кодом."""
    with (
        patch('app.run.sys.argv', ['app.run.py', 'parse', '--json']),
        patch('app.run.init_cfg'),
        patch('app.run.fail_unknown_result_template', return_value=None) as mock_fail,
        patch('app.run.machine_json', return_value=0) as mock_json,
        patch('app.run.sys.exit', side_effect=SystemExit(0)) as mock_exit,
    ):
        from app.run import main

        with pytest.raises(SystemExit):
            main()

        mock_fail.assert_called_once_with('parse', None, json_mode=True)
        mock_json.assert_called_once_with('parse', all_result=False, result_template=None, payload_arg=None)
        mock_exit.assert_called_with(0)


def test_run_machine_json_all_result_dispatch() -> None:
    """parse --json --all-result передаёт all_result=True."""
    with (
        patch('app.run.sys.argv', ['app.run.py', 'parse', '--json', '--all-result']),
        patch('app.run.init_cfg'),
        patch('app.run.machine_json', return_value=0) as mock_json,
        patch('app.run.sys.exit', side_effect=SystemExit(0)),
    ):
        from app.run import main

        with pytest.raises(SystemExit):
            main()

        mock_json.assert_called_once_with('parse', all_result=True, result_template=None, payload_arg=None)


def test_run_machine_human_parse() -> None:
    """parse без --json вызывает try_call с формированием прайса."""
    with (
        patch('app.run.sys.argv', ['app.run.py', 'parse']),
        patch('app.run.init_cfg'),
        patch('app.run.try_call') as mock_try,
        patch('app.run.sys.exit', side_effect=SystemExit(0)),
    ):
        from app.run import main

        with pytest.raises(SystemExit):
            main()

        mock_try.assert_called_once()
        assert mock_try.call_args.args[0].__name__ == 'run_make_price_by_supplier'
        assert mock_try.call_args.kwargs == {'result_template': None}


def test_run_machine_human_doubles() -> None:
    """doubles без --json вызывает отчёт о дублях."""
    with (
        patch('app.run.sys.argv', ['app.run.py', 'doubles']),
        patch('app.run.init_cfg'),
        patch('app.run.try_call') as mock_try,
        patch('app.run.sys.exit', side_effect=SystemExit(0)),
    ):
        from app.run import main

        with pytest.raises(SystemExit):
            main()

        assert mock_try.call_args.args[0].__name__ == 'run_report_doubles'


def test_run_machine_human_zapaska() -> None:
    """zapaska без --json вызывает выгрузку API."""
    with (
        patch('app.run.sys.argv', ['app.run.py', 'zapaska_load_api_data']),
        patch('app.run.init_cfg'),
        patch('app.run.try_call') as mock_try,
        patch('app.run.sys.exit', side_effect=SystemExit(0)),
    ):
        from app.run import main

        with pytest.raises(SystemExit):
            main()

        assert mock_try.call_args.args[0].__name__ == 'run_upload_zapaska_data'


def test_run_machine_human_mim() -> None:
    """mim_load_api_data без --json вызывает выгрузку МИМ."""
    with (
        patch('app.run.sys.argv', ['app.run.py', 'mim_load_api_data']),
        patch('app.run.init_cfg'),
        patch('app.run.try_call') as mock_try,
        patch('app.run.sys.exit', side_effect=SystemExit(0)),
    ):
        from app.run import main

        with pytest.raises(SystemExit):
            main()

        assert mock_try.call_args.args[0].__name__ == 'run_upload_mim_data'


def test_run_machine_human_four_tochki() -> None:
    """four_tochki_load_api_data без --json вызывает выгрузку Форточек."""
    with (
        patch('app.run.sys.argv', ['app.run.py', 'four_tochki_load_api_data']),
        patch('app.run.init_cfg'),
        patch('app.run.try_call') as mock_try,
        patch('app.run.sys.exit', side_effect=SystemExit(0)),
    ):
        from app.run import main

        with pytest.raises(SystemExit):
            main()

        assert mock_try.call_args.args[0].__name__ == 'run_upload_four_tochki_data'


def test_run_machine_human_fetch_mail() -> None:
    """fetch_mail_prices без --json вызывает выгрузку из почты."""
    with (
        patch('app.run.sys.argv', ['app.run.py', 'fetch_mail_prices']),
        patch('app.run.init_cfg'),
        patch('app.run.try_call') as mock_try,
        patch('app.run.sys.exit', side_effect=SystemExit(0)),
    ):
        from app.run import main

        with pytest.raises(SystemExit):
            main()

        assert mock_try.call_args.args[0].__name__ == 'run_fetch_mail_prices'


def test_run_machine_json_get_supliers() -> None:
    """get_supliers без --json всё равно уходит в JSON-режим."""
    with (
        patch('app.run.sys.argv', ['app.run.py', 'get_supliers']),
        patch('app.run.init_cfg'),
        patch('app.run.machine_json', return_value=0) as mock_json,
        patch('app.run.sys.exit', side_effect=SystemExit(0)),
    ):
        from app.run import main

        with pytest.raises(SystemExit):
            main()

        mock_json.assert_called_once_with(
            'get_supliers',
            all_result=False,
            result_template=None,
            payload_arg=None,
        )


def test_run_machine_json_toggle_vendor_passes_folder() -> None:
    """toggle_vendor уходит в JSON-режим с папкой поставщика."""
    with (
        patch('app.run.sys.argv', ['app.run.py', 'toggle_vendor', 'poshk']),
        patch('app.run.init_cfg'),
        patch('app.run.machine_json', return_value=0) as mock_json,
        patch('app.run.sys.exit', side_effect=SystemExit(0)),
    ):
        from app.run import main

        with pytest.raises(SystemExit):
            main()

        mock_json.assert_called_once_with(
            'toggle_vendor',
            all_result=False,
            result_template=None,
            payload_arg='poshk',
        )


def test_run_machine_rejects_non_str_command() -> None:
    """если argparse не выставил command — код 1."""
    args = MagicMock(command=None, json=False, all_result=False)
    with (
        patch('app.run.sys.argv', ['app.run.py', 'parse']),
        patch('app.run.init_cfg'),
        patch('app.run.parse_machine_args', return_value=args),
        patch('app.run.sys.exit', side_effect=SystemExit(1)) as mock_exit,
    ):
        from app.run import main

        with pytest.raises(SystemExit) as exit_info:
            main()

        assert exit_info.value.code == 1
        mock_exit.assert_called_with(1)


def test_run_machine_all_result_implies_json() -> None:
    """parse --all-result без --json всё равно уходит в JSON-режим."""
    with (
        patch('app.run.sys.argv', ['app.run.py', 'parse', '--all-result']),
        patch('app.run.init_cfg'),
        patch('app.run.machine_json', return_value=0) as mock_json,
        patch('app.run.sys.exit', side_effect=SystemExit(0)),
    ):
        from app.run import main

        with pytest.raises(SystemExit):
            main()

        mock_json.assert_called_once_with('parse', all_result=True, result_template=None, payload_arg=None)


def test_clear_result_command_removes_only_results(
    fake_config_provider: FakeConfigProvider, capsys: pytest.CaptureFixture[str]
) -> None:
    """Самостоятельная команда очищает результаты и отдаёт JSON без флага."""
    from app.run import main

    output_folder = Path(fake_config_provider.result_folder())
    nested = output_folder / 'nested'
    nested.mkdir()
    (nested / 'report.jsonl').touch()
    (output_folder / 'result_meta.json').touch()
    price = Path(fake_config_provider.price_folder('mim')) / 'price.xlsx'
    price.parent.mkdir()
    price.touch()

    with (
        patch('app.run.sys.argv', ['pf', 'clear_result']),
        patch('app.run.init_cfg'),
        pytest.raises(SystemExit) as stopped,
    ):
        main()

    assert stopped.value.code == 0
    assert output_folder.is_dir()
    assert not list(output_folder.iterdir())
    assert price.is_file()
    payload = json.loads(capsys.readouterr().out)
    assert payload['ok'] is True
    assert payload['action'] == 'clear_result'


def test_run_machine_clears_result_folder() -> None:
    """--clear-previous-result очищает result до команды."""
    with (
        patch('app.run.sys.argv', ['app.run.py', 'parse', '--json', '--clear-previous-result']),
        patch('app.run.init_cfg'),
        patch('app.run.clear_result_folder') as mock_clear,
        patch('app.run.machine_json', return_value=0) as mock_json,
        patch('app.run.sys.exit', side_effect=SystemExit(0)),
    ):
        from app.run import main

        with pytest.raises(SystemExit):
            main()

        mock_clear.assert_called_once()
        mock_json.assert_called_once_with('parse', all_result=False, result_template=None, payload_arg=None)


def test_run_machine_skips_clear_without_flag() -> None:
    """без флага папка result не чистится."""
    with (
        patch('app.run.sys.argv', ['app.run.py', 'parse', '--json']),
        patch('app.run.init_cfg'),
        patch('app.run.clear_result_folder') as mock_clear,
        patch('app.run.machine_json', return_value=0),
        patch('app.run.sys.exit', side_effect=SystemExit(0)),
    ):
        from app.run import main

        with pytest.raises(SystemExit):
            main()

        mock_clear.assert_not_called()


def test_json_passes_result_template() -> None:
    """parse --json --result-template передаёт имя шаблона."""
    with (
        patch('app.run.sys.argv', ['app.run.py', 'parse', '--json', '--result-template', 'for_drom']),
        patch('app.run.init_cfg'),
        patch('app.run.machine_json', return_value=0) as mock_json,
        patch('app.run.sys.exit', side_effect=SystemExit(0)),
    ):
        from app.run import main

        with pytest.raises(SystemExit):
            main()

        mock_json.assert_called_once_with(
            'parse',
            all_result=False,
            result_template='for_drom',
            payload_arg=None,
        )


def test_run_machine_human_result_template() -> None:
    """parse --result-template без --json передаёт имя в try_call."""
    with (
        patch('app.run.sys.argv', ['app.run.py', 'parse', '--result-template', 'for_inner']),
        patch('app.run.init_cfg'),
        patch('app.run.try_call') as mock_try,
        patch('app.run.sys.exit', side_effect=SystemExit(0)),
    ):
        from app.run import main

        with pytest.raises(SystemExit):
            main()

        assert mock_try.call_args.kwargs == {'result_template': 'for_inner'}


def test_run_machine_unknown_template_json(capsys: pytest.CaptureFixture[str]) -> None:
    """неизвестный шаблон в JSON-режиме: ошибка, без разбора."""
    with (
        patch('app.run.sys.argv', ['app.run.py', 'parse', '--json', '--result-template', 'nope']),
        patch('app.run.init_cfg'),
        patch('app.run.machine_json') as mock_json,
        patch('app.run.clear_result_folder') as mock_clear,
        patch('app.run.sys.exit', side_effect=SystemExit(1)) as mock_exit,
    ):
        from app.run import main

        with pytest.raises(SystemExit) as exit_info:
            main()

        assert exit_info.value.code == 1
        mock_exit.assert_called_with(1)
        mock_json.assert_not_called()
        mock_clear.assert_not_called()
    payload = json.loads(capsys.readouterr().out)
    assert payload['ok'] is False
    assert payload['error']['kind'] == 'UnknownWriterTemplateError'
    assert 'nope' in payload['error']['message']
    assert payload['elapsed_seconds'] >= 0


def test_run_machine_unknown_template_human(capsys: pytest.CaptureFixture[str]) -> None:
    """неизвестный шаблон без --json: ошибка, без разбора."""
    with (
        patch('app.run.sys.argv', ['app.run.py', 'parse', '--result-template', 'nope']),
        patch('app.run.init_cfg'),
        patch('app.run.try_call') as mock_try,
        patch('app.run.sys.exit', side_effect=SystemExit(1)) as mock_exit,
    ):
        from app.run import main

        with pytest.raises(SystemExit) as exit_info:
            main()

        assert exit_info.value.code == 1
        mock_exit.assert_called_with(1)
        mock_try.assert_not_called()
    assert 'nope' in capsys.readouterr().out


def test_unknown_template_does_not_clear_result() -> None:
    """ошибка шаблона не чистит result даже с --clear-previous-result."""
    with (
        patch(
            'app.run.sys.argv',
            ['app.run.py', 'parse', '--json', '--clear-previous-result', '--result-template', 'nope'],
        ),
        patch('app.run.init_cfg'),
        patch('app.run.clear_result_folder') as mock_clear,
        patch('app.run.machine_json') as mock_json,
        patch('app.run.sys.exit', side_effect=SystemExit(1)),
    ):
        from app.run import main

        with pytest.raises(SystemExit):
            main()

        mock_clear.assert_not_called()
        mock_json.assert_not_called()


def test_run_machine_human_failure_exit_code() -> None:
    """parse без --json: ошибка домена из try_call даёт ненулевой код возврата."""
    with (
        patch('app.run.sys.argv', ['app.run.py', 'parse']),
        patch('app.run.init_cfg'),
        patch('app.run.try_call', return_value=False),
        patch('app.run.sys.exit', side_effect=SystemExit(1)) as mock_exit,
    ):
        from app.run import main

        with pytest.raises(SystemExit):
            main()

        mock_exit.assert_called_once_with(1)
