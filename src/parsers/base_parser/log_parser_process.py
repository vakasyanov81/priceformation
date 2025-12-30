"""
logging parse process
"""

from typing import Optional


from core.log_message import log_msg, warn_msg

from .parse_statistic import ParseResultStatistic


def _log_msg(msg: str) -> None:
    """log msg"""
    log_msg(msg, need_print_log=True)


class LoggerParseProcess:
    """logging parse process"""

    def __init__(self, parser_repr: str) -> None:
        """init"""

        self.parser_repr: str = parser_repr

    def log_start(self) -> None:
        """logging start parse process"""

        _log_msg(f"{self.parser_repr} // старт")

    def log_finish(self, result_statistic: Optional[ParseResultStatistic] = None) -> None:
        """logging finish parse process"""

        if result_statistic:

            min_percent, max_percent = result_statistic.real_percents_markup()

            min_margin, max_margin = result_statistic.real_absolute_markup()

            _log_msg(f"Обработано позиций - {result_statistic.count_items()} ")

            _log_msg(f"Наценка (%) - Мин: {min_percent}, Макс: {max_percent} ")

            _log_msg(f"Наценка (Руб.) - Мин: {min_margin}, Макс: {max_margin} ")

            _log_msg(f"{self.parser_repr} // финиш")
        _log_msg("--------------------------------------------------------")

    @classmethod
    def log_list_files(cls, files) -> None:
        """logging files list"""

        _log_msg(f"список файлов для обработки - {files}")

    def log_disable_status(self) -> None:
        """logging disabled"""

        warn_msg(f"поставщик {self.parser_repr} не активен", need_print_log=True)

        self.log_finish()
