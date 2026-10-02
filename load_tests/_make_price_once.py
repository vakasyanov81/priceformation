"""Один прогон пункта 1. Пишет секунды в файл из argv[2]."""

import sys
import time
from pathlib import Path

from cfg import init_cfg
from infrastructure.config.fake_config_provider import FakeConfigProvider
from infrastructure.config.file_config_provider import FileConfigProvider
from run import run_make_price_by_supplier
from services.configure import configure_services


def main() -> None:
    result_dir = Path(sys.argv[1]).resolve()
    elapsed_path = Path(sys.argv[2])
    init_cfg(FakeConfigProvider(Path(FileConfigProvider().project_root), result_folder=result_dir))
    configure_services()

    start = time.perf_counter()
    run_make_price_by_supplier()
    elapsed = time.perf_counter() - start
    elapsed_path.write_text(f'{elapsed:.6f}', encoding='utf-8')


if __name__ == '__main__':
    main()
