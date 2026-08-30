"""Диспетчер неинтерактивных команд run.main."""

import json
from unittest.mock import MagicMock, patch

import pytest


def test_run_machine_json_dispatch() -> None:
    """parse --json уходит в machine_json и завершает процесс его кодом."""
    with (
        patch("run.sys.argv", ["run.py", "parse", "--json"]),
        patch("run.init_cfg"),
        patch("run.machine_json", return_value=0) as mock_json,
        patch("run.sys.exit", side_effect=SystemExit(0)) as mock_exit,
    ):
        from run import main

        with pytest.raises(SystemExit):
            main()

        mock_json.assert_called_once_with("parse", all_result=False, result_template=None, supplier_prices=None)
        mock_exit.assert_called_with(0)


def test_run_machine_json_all_result_dispatch() -> None:
    """parse --json --all-result передаёт all_result=True."""
    with (
        patch("run.sys.argv", ["run.py", "parse", "--json", "--all-result"]),
        patch("run.init_cfg"),
        patch("run.machine_json", return_value=0) as mock_json,
        patch("run.sys.exit", side_effect=SystemExit(0)),
    ):
        from run import main

        with pytest.raises(SystemExit):
            main()

        mock_json.assert_called_once_with("parse", all_result=True, result_template=None, supplier_prices=None)


def test_run_machine_human_parse() -> None:
    """parse без --json вызывает try_call с формированием прайса."""
    with (
        patch("run.sys.argv", ["run.py", "parse"]),
        patch("run.init_cfg"),
        patch("run.try_call") as mock_try,
        patch("run.sys.exit", side_effect=SystemExit(0)),
    ):
        from run import main

        with pytest.raises(SystemExit):
            main()

        mock_try.assert_called_once()
        assert mock_try.call_args.args[0].__name__ == "run_make_price_by_supplier"
        assert mock_try.call_args.kwargs == {"result_template": None}


def test_run_machine_human_doubles() -> None:
    """doubles без --json вызывает отчёт о дублях."""
    with (
        patch("run.sys.argv", ["run.py", "doubles"]),
        patch("run.init_cfg"),
        patch("run.try_call") as mock_try,
        patch("run.sys.exit", side_effect=SystemExit(0)),
    ):
        from run import main

        with pytest.raises(SystemExit):
            main()

        assert mock_try.call_args.args[0].__name__ == "run_report_doubles"


def test_run_machine_human_zapaska() -> None:
    """zapaska без --json вызывает выгрузку API."""
    with (
        patch("run.sys.argv", ["run.py", "zapaska"]),
        patch("run.init_cfg"),
        patch("run.try_call") as mock_try,
        patch("run.sys.exit", side_effect=SystemExit(0)),
    ):
        from run import main

        with pytest.raises(SystemExit):
            main()

        assert mock_try.call_args.args[0].__name__ == "run_upload_zapaska_data"


def test_run_machine_json_get_supliers() -> None:
    """get_supliers без --json всё равно уходит в JSON-режим."""
    with (
        patch("run.sys.argv", ["run.py", "get_supliers"]),
        patch("run.init_cfg"),
        patch("run.machine_json", return_value=0) as mock_json,
        patch("run.sys.exit", side_effect=SystemExit(0)),
    ):
        from run import main

        with pytest.raises(SystemExit):
            main()

        mock_json.assert_called_once_with("get_supliers", all_result=False, result_template=None, supplier_prices=None)


def test_run_machine_rejects_non_str_command() -> None:
    """если argparse не выставил command — код 1."""
    args = MagicMock(command=None, json=False, all_result=False)
    with (
        patch("run.sys.argv", ["run.py", "parse"]),
        patch("run.init_cfg"),
        patch("run.parse_machine_args", return_value=args),
        patch("run.sys.exit", side_effect=SystemExit(1)) as mock_exit,
    ):
        from run import main

        with pytest.raises(SystemExit) as exit_info:
            main()

        assert exit_info.value.code == 1
        mock_exit.assert_called_with(1)


def test_run_machine_all_result_implies_json() -> None:
    """parse --all-result без --json всё равно уходит в JSON-режим."""
    with (
        patch("run.sys.argv", ["run.py", "parse", "--all-result"]),
        patch("run.init_cfg"),
        patch("run.machine_json", return_value=0) as mock_json,
        patch("run.sys.exit", side_effect=SystemExit(0)),
    ):
        from run import main

        with pytest.raises(SystemExit):
            main()

        mock_json.assert_called_once_with("parse", all_result=True, result_template=None, supplier_prices=None)


def test_run_machine_clears_result_folder() -> None:
    """--clear-previous-result очищает result до команды."""
    with (
        patch("run.sys.argv", ["run.py", "parse", "--json", "--clear-previous-result"]),
        patch("run.init_cfg"),
        patch("run.clear_result_folder") as mock_clear,
        patch("run.machine_json", return_value=0) as mock_json,
        patch("run.sys.exit", side_effect=SystemExit(0)),
    ):
        from run import main

        with pytest.raises(SystemExit):
            main()

        mock_clear.assert_called_once()
        mock_json.assert_called_once_with("parse", all_result=False, result_template=None, supplier_prices=None)


def test_run_machine_skips_clear_without_flag() -> None:
    """без флага папка result не чистится."""
    with (
        patch("run.sys.argv", ["run.py", "parse", "--json"]),
        patch("run.init_cfg"),
        patch("run.clear_result_folder") as mock_clear,
        patch("run.machine_json", return_value=0),
        patch("run.sys.exit", side_effect=SystemExit(0)),
    ):
        from run import main

        with pytest.raises(SystemExit):
            main()

        mock_clear.assert_not_called()


def test_json_passes_result_template() -> None:
    """parse --json --result-template передаёт имя шаблона."""
    with (
        patch("run.sys.argv", ["run.py", "parse", "--json", "--result-template", "for_drom"]),
        patch("run.init_cfg"),
        patch("run.machine_json", return_value=0) as mock_json,
        patch("run.sys.exit", side_effect=SystemExit(0)),
    ):
        from run import main

        with pytest.raises(SystemExit):
            main()

        mock_json.assert_called_once_with("parse", all_result=False, result_template="for_drom", supplier_prices=None)


def test_run_machine_human_result_template() -> None:
    """parse --result-template без --json передаёт имя в try_call."""
    with (
        patch("run.sys.argv", ["run.py", "parse", "--result-template", "for_inner"]),
        patch("run.init_cfg"),
        patch("run.try_call") as mock_try,
        patch("run.sys.exit", side_effect=SystemExit(0)),
    ):
        from run import main

        with pytest.raises(SystemExit):
            main()

        assert mock_try.call_args.kwargs == {"result_template": "for_inner"}


def test_run_machine_unknown_template_json(capsys: pytest.CaptureFixture[str]) -> None:
    """неизвестный шаблон в JSON-режиме: ошибка, без разбора."""
    with (
        patch("run.sys.argv", ["run.py", "parse", "--json", "--result-template", "nope"]),
        patch("run.init_cfg"),
        patch("run.machine_json") as mock_json,
        patch("run.clear_result_folder") as mock_clear,
        patch("run.sys.exit", side_effect=SystemExit(1)) as mock_exit,
    ):
        from run import main

        with pytest.raises(SystemExit) as exit_info:
            main()

        assert exit_info.value.code == 1
        mock_exit.assert_called_with(1)
        mock_json.assert_not_called()
        mock_clear.assert_not_called()
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is False
    assert payload["error"]["kind"] == "UnknownWriterTemplateError"
    assert "nope" in payload["error"]["message"]


def test_run_machine_unknown_template_human(capsys: pytest.CaptureFixture[str]) -> None:
    """неизвестный шаблон без --json: ошибка, без разбора."""
    with (
        patch("run.sys.argv", ["run.py", "parse", "--result-template", "nope"]),
        patch("run.init_cfg"),
        patch("run.try_call") as mock_try,
        patch("run.sys.exit", side_effect=SystemExit(1)) as mock_exit,
    ):
        from run import main

        with pytest.raises(SystemExit) as exit_info:
            main()

        assert exit_info.value.code == 1
        mock_exit.assert_called_with(1)
        mock_try.assert_not_called()
    assert "nope" in capsys.readouterr().out


def test_unknown_template_does_not_clear_result() -> None:
    """ошибка шаблона не чистит result даже с --clear-previous-result."""
    with (
        patch(
            "run.sys.argv",
            ["run.py", "parse", "--json", "--clear-previous-result", "--result-template", "nope"],
        ),
        patch("run.init_cfg"),
        patch("run.clear_result_folder") as mock_clear,
        patch("run.machine_json") as mock_json,
        patch("run.sys.exit", side_effect=SystemExit(1)),
    ):
        from run import main

        with pytest.raises(SystemExit):
            main()

        mock_clear.assert_not_called()
        mock_json.assert_not_called()
