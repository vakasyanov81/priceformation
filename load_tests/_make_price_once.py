"""Один прогон пункта 1. Пишет секунды в файл из argv[2]."""

import sys
import time
from pathlib import Path

from cfg import init_cfg
from core.parse_paths import ParsePaths, configure_parse_paths, get_parse_paths
from run import run_make_price_by_supplier


def main() -> None:
    init_cfg()
    result_dir = Path(sys.argv[1]).resolve()
    elapsed_path = Path(sys.argv[2])
    paths = get_parse_paths()
    configure_parse_paths(
        ParsePaths(
            file_prices_folder=paths.file_prices_folder,
            user_config_folder=paths.user_config_folder,
            result_folder=f"{result_dir}/",
        ),
    )

    start = time.perf_counter()
    run_make_price_by_supplier()
    elapsed = time.perf_counter() - start
    elapsed_path.write_text(f"{elapsed:.6f}", encoding="utf-8")


if __name__ == "__main__":
    main()
