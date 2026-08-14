"""Integration tests for mutmut stats collection and CLI."""

from io import StringIO
from pathlib import Path

from test_pipelines.tiny_mutants import write_tiny_mutants

from pipelines.mutmut_stats.aggregate import build_analysis
from pipelines.mutmut_stats.cli import main
from pipelines.mutmut_stats.report import render_json, render_markdown


def test_analysis_is_deterministic(tmp_path: Path) -> None:
    mutants_dir = write_tiny_mutants(tmp_path)
    first = render_json(build_analysis(mutants_dir))
    second = render_json(build_analysis(mutants_dir))
    assert first == second
    assert render_markdown(build_analysis(mutants_dir)) == render_markdown(build_analysis(mutants_dir))


def test_analysis_groups_survivors(tmp_path: Path) -> None:
    analysis = build_analysis(write_tiny_mutants(tmp_path))
    summary = dict(analysis.summary)
    assert summary["total"] == 3
    assert summary["survived"] == 1
    assert summary["killed"] == 1
    assert summary["no tests"] == 1
    assert analysis.mutation_score == 0.5
    assert analysis.interesting[0].function == "add"
    assert analysis.interesting[0].kind == "operator"
    assert analysis.interesting[0].change == "== → !="
    assert analysis.interesting[0].tests == (
        "tests/test_sample.py::test_add_a",
        "tests/test_sample.py::test_add_b",
    )
    assert analysis.interesting[1].function == "mul"
    assert analysis.interesting[1].status == "no tests"
    assert analysis.interesting[1].tests == ()


def test_markdown_contains_sections(tmp_path: Path) -> None:
    markdown = render_markdown(build_analysis(write_tiny_mutants(tmp_path)))
    assert "## Сводка" in markdown
    assert "## Выжившие по файлам" in markdown
    assert "## Одинаковые изменения" in markdown
    assert "`== → !=`" in markdown
    assert "```diff" in markdown


def test_cli_writes_reports(tmp_path: Path) -> None:
    mutants_dir = write_tiny_mutants(tmp_path)
    output_dir = tmp_path / "out"
    stdout = StringIO()
    code = main(
        ["--mutants-dir", str(mutants_dir), "--output-dir", str(output_dir)],
        stdout=stdout,
    )
    assert code == 0
    brief = stdout.getvalue()
    assert "survived: 1" in brief
    markdown = (output_dir / "mutmut-analysis.md").read_text(encoding="utf-8")
    payload = (output_dir / "mutmut-analysis.json").read_text(encoding="utf-8")
    assert markdown == render_markdown(build_analysis(mutants_dir))
    assert payload == render_json(build_analysis(mutants_dir))


def test_cli_stdout_and_missing_dir(tmp_path: Path) -> None:
    mutants_dir = write_tiny_mutants(tmp_path)
    stdout = StringIO()
    code = main(["--mutants-dir", str(mutants_dir), "--stdout"], stdout=stdout)
    assert code == 0
    assert stdout.getvalue().startswith("# Статистика mutmut")
    missing = StringIO()
    assert main(["--mutants-dir", str(tmp_path / "absent")], stdout=missing) == 1
    assert "Нет каталога" in missing.getvalue()


def test_empty_mutants_dir(tmp_path: Path) -> None:
    mutants_dir = tmp_path / "mutants"
    mutants_dir.mkdir()
    analysis = build_analysis(mutants_dir)
    assert analysis.mutation_score == 0.0
    assert dict(analysis.summary) == {"total": 0}
    markdown = render_markdown(analysis)
    assert "Нет записей" in markdown
    assert "Нет выживших" in markdown
