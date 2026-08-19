"""
Нагрузка пункта 1: общий прайс по прайсам поставщиков.

Запуск (не входит в обычный pytest):

    uv run pytest load_tests -n0
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_PRICES = _PROJECT_ROOT / "file_prices"
_REQUIRED_PRICES = (
    _PRICES / "zapaska" / "tire.json",
    _PRICES / "zapaska" / "disk.json",
    _PRICES / "mim" / "price.xlsx",
    _PRICES / "four_tochki" / "price.xlsx",
)
_RUNNER = Path(__file__).with_name("_make_price_once.py")

# Три изолированных прогона 2026-08-19 на текущих file_prices: 5.02 / 4.99 / 4.98 с.
_MEASURED_SECONDS = 5.0
_HEADROOM = 1.3
MAX_MAKE_PRICE_SECONDS = _MEASURED_SECONDS * _HEADROOM


def _local_prices_present() -> bool:
    return all(path.is_file() for path in _REQUIRED_PRICES)


def _child_env() -> dict[str, str]:
    env = os.environ.copy()
    pythonpath = [str(_PROJECT_ROOT / "src")]
    inherited = env.get("PYTHONPATH")
    if inherited:
        pythonpath.append(inherited)
    env["PYTHONPATH"] = os.pathsep.join(pythonpath)
    return env


def _run_make_price(result_dir: Path, elapsed_file: Path) -> None:
    subprocess.run(  # noqa: S603
        [sys.executable, str(_RUNNER), str(result_dir), str(elapsed_file)],
        check=True,
        cwd=_PROJECT_ROOT,
        env=_child_env(),
    )


@pytest.mark.skipif(
    not _local_prices_present(),
    reason="нужны локальные file_prices (каталог в .gitignore)",
)
def test_make_price_within_budget(tmp_path: Path) -> None:
    """Пункт 1 CLI укладывается в эталон с запасом 30%."""
    result_dir = tmp_path / "result"
    result_dir.mkdir()
    elapsed_file = tmp_path / "elapsed.txt"
    _run_make_price(result_dir, elapsed_file)
    elapsed = float(elapsed_file.read_text(encoding="utf-8"))
    written = list(result_dir.glob("*.xlsx"))
    assert written, "ожидались xlsx в временной папке результата"
    budget = MAX_MAKE_PRICE_SECONDS
    assert elapsed <= budget, "пункт 1 занял {0:.2f} с при бюджете {1:.1f} с".format(elapsed, budget)
