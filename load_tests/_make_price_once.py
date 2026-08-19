"""Один прогон пункта 1. Пишет секунды в файл из argv[2]."""

import sys
import time
from pathlib import Path
from unittest.mock import patch

from cfg import init_cfg
from cfg.main import MainConfig
from run import run_make_price_by_supplier


def main() -> None:
    init_cfg()
    result_dir = Path(sys.argv[1]).resolve()
    result_folder = "{0}/".format(result_dir)
    elapsed_path = Path(sys.argv[2])

    def _result_folder(_cfg: MainConfig) -> str:
        return result_folder

    start = time.perf_counter()
    with patch.object(MainConfig, "result_folder_path", property(_result_folder)):
        run_make_price_by_supplier()
    elapsed = time.perf_counter() - start
    elapsed_path.write_text("{0:.6f}".format(elapsed), encoding="utf-8")


if __name__ == "__main__":
    main()
