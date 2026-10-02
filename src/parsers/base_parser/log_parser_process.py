"""
logging parse process
"""

import logging

from .parse_statistic import ParseResultStatistic

logger = logging.getLogger(__name__)


class LoggerParseProcess:
    """logging parse process"""

    def __init__(self, parser_repr: str) -> None:
        """init"""

        self.parser_repr: str = parser_repr

    def log_start(self) -> None:
        """logging start parse process"""

        logger.info(f'{self.parser_repr} // старт')

    def log_finish(self, result_statistic: ParseResultStatistic | None = None) -> None:
        """logging finish parse process"""
        if result_statistic:
            min_percent, max_percent = result_statistic.real_percents_markup()
            min_margin, max_margin = result_statistic.real_absolute_markup()
            logger.info(f'Обработано позиций - {result_statistic.count_items()} ')
            logger.info(f'Наценка (%) - Мин: {min_percent}, Макс: {max_percent} ')
            logger.info(f'Наценка (Руб.) - Мин: {min_margin}, Макс: {max_margin} ')
            logger.info(f'{self.parser_repr} // финиш')
        logger.info('--------------------------------------------------------')

    @classmethod
    def log_list_files(cls, files: list[str]) -> None:
        """logging files list"""

        logger.info(f'список файлов для обработки - {files}')

    def log_disable_status(self) -> None:
        """logging disabled"""
        logger.warning(f'поставщик {self.parser_repr} не активен')
        self.log_finish()
