"""CLI for mutmut survivor statistics."""

import argparse
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO

from .aggregate import build_analysis
from .models import Analysis
from .report import render_json, render_markdown

_MD_NAME = "mutmut-analysis.md"
_JSON_NAME = "mutmut-analysis.json"


@dataclass(frozen=True)
class CliOptions:
    """Parsed CLI flags."""

    mutants_dir: Path
    output_dir: Path | None
    stdout_report: bool


def main(argv: Sequence[str] | None = None, stdout: TextIO | None = None) -> int:
    """Parse args, write reports, return process exit code."""
    output = stdout if stdout is not None else sys.stdout
    options = _parse_args(argv)
    mutants_dir = options.mutants_dir.resolve()
    if not mutants_dir.is_dir():
        output.write(f"Нет каталога {mutants_dir}. Сначала выполните: uv run mutmut run\n")
        return 1
    analysis = build_analysis(mutants_dir)
    output_dir = _write_reports(options, analysis, mutants_dir)
    _write_user_output(options, analysis, output_dir, output)
    return 0


def _parse_args(argv: Sequence[str] | None) -> CliOptions:
    parser = argparse.ArgumentParser(
        description="Собрать детерминированную статистику выживших мутантов mutmut.",
    )
    parser.add_argument(
        "--mutants-dir",
        type=Path,
        default=Path("mutants"),
        help="Каталог с результатами mutmut (по умолчанию: mutants)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Куда писать mutmut-analysis.md и .json (по умолчанию: --mutants-dir)",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Печатать полный markdown-отчёт в stdout вместо краткой сводки",
    )
    namespace = parser.parse_args(argv)
    return CliOptions(
        mutants_dir=namespace.mutants_dir,
        output_dir=namespace.output_dir,
        stdout_report=namespace.stdout,
    )


def _write_reports(options: CliOptions, analysis: Analysis, mutants_dir: Path) -> Path:
    output_dir = (options.output_dir or mutants_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / _MD_NAME).write_text(render_markdown(analysis), encoding="utf-8")
    (output_dir / _JSON_NAME).write_text(render_json(analysis), encoding="utf-8")
    return output_dir


def _write_user_output(
    options: CliOptions,
    analysis: Analysis,
    output_dir: Path,
    stdout: TextIO,
) -> None:
    if options.stdout_report:
        stdout.write(render_markdown(analysis))
        return
    _write_brief(analysis, output_dir, stdout)


def _write_brief(analysis: Analysis, output_dir: Path, stdout: TextIO) -> None:
    summary = dict(analysis.summary)
    survived = summary.get("survived", 0)
    total = summary.get("total", 0)
    percent = f"{analysis.mutation_score * 100:.1f}"
    md_path = (output_dir / _MD_NAME).as_posix()
    json_path = (output_dir / _JSON_NAME).as_posix()
    stdout.write(
        f"mutants: {total}; survived: {survived}; score: {percent}%\n"
        f"written: {md_path}\n"
        f"written: {json_path}\n",
    )
