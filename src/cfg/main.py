"""
main configuration
"""

import datetime
import os
import pathlib

__LOG_FOLDER__ = "logs"
__USER_PARSE_CONFIG__ = "parse_config"
__FILE_PRICES__ = "file_prices"
__FILE_PRICES_RESULT__ = "result"
__VENDOR_LIST_FILE_NAME__ = "vendor_list.json"
__MARKUP_RULES_FILE_NAME__ = "markup_rules.json"
__MANUFACTURER_ALIASES_FILE_NAME__ = "manufacturer_aliases.json"
__TITLE_ALIASES_FILE_NAME__ = "title_aliases.json"
__BLACK_LIST_FILE_NAME__ = "black_list"
__STOP_WORDS_FILE_NAME__ = "stop_words"

__PROJECT_ROOT__ = str(pathlib.Path(__file__).parent.parent.parent.absolute())
__PROJECT_SRC__ = str(pathlib.Path(__file__).parent.parent.absolute())

__IS_NEED_PRINT_LOG__ = True

_USER_CONFIG_FOLDER_PATH = __PROJECT_ROOT__ + os.sep + __USER_PARSE_CONFIG__ + os.sep
_LOG_FOLDER_PATH = __PROJECT_ROOT__ + os.sep + __LOG_FOLDER__
_RESULT_FOLDER_PATH = f"{__PROJECT_ROOT__}{os.sep}file_prices{os.sep}result{os.sep}"


class MainCfg:
    """main configuration property container"""

    folder_file_prices = __FILE_PRICES__
    folder_file_prices_result = f"{__FILE_PRICES__}{os.sep}{__FILE_PRICES_RESULT__}"
    vendor_list_file_name = __VENDOR_LIST_FILE_NAME__
    markup_rules_file_name = __MARKUP_RULES_FILE_NAME__
    black_list_file_name = __BLACK_LIST_FILE_NAME__
    stop_words_file_name = __STOP_WORDS_FILE_NAME__
    user_config_folder_name = __USER_PARSE_CONFIG__
    manufacturer_aliases_file_name = __MANUFACTURER_ALIASES_FILE_NAME__
    title_aliases_file_name = __TITLE_ALIASES_FILE_NAME__
    user_config_folder_path = _USER_CONFIG_FOLDER_PATH
    manufacturer_aliases_file_path = _USER_CONFIG_FOLDER_PATH + __MANUFACTURER_ALIASES_FILE_NAME__
    title_aliases_file_path = _USER_CONFIG_FOLDER_PATH + __TITLE_ALIASES_FILE_NAME__
    markup_rules_file_path = _USER_CONFIG_FOLDER_PATH + __MARKUP_RULES_FILE_NAME__
    black_list_file_path = _USER_CONFIG_FOLDER_PATH + __BLACK_LIST_FILE_NAME__
    stop_words_file_path = _USER_CONFIG_FOLDER_PATH + __STOP_WORDS_FILE_NAME__
    vendor_list_file_path = _USER_CONFIG_FOLDER_PATH + __VENDOR_LIST_FILE_NAME__


class MainConfig(MainCfg):
    """main configuration property container"""

    project_root = __PROJECT_ROOT__
    project_src = __PROJECT_SRC__
    sep = os.sep
    log_folder_name = __LOG_FOLDER__
    log_folder_path = _LOG_FOLDER_PATH
    result_folder_path = _RESULT_FOLDER_PATH
    is_need_print_log = __IS_NEED_PRINT_LOG__

    @property
    def current_log_file_name(self) -> str:
        """current log file name"""
        today = datetime.date.today()
        return f"log_{today}.log"

    @property
    def current_err_log_file_name(self) -> str:
        """current log-error file name"""
        today = datetime.date.today()
        return f"error_{today}.log"

    @property
    def current_log_file_path(self) -> str:
        """path to current log file"""
        return self.log_folder_path + self.sep + self.current_log_file_name

    @property
    def current_err_log_file_path(self) -> str:
        """path to current log-error file"""
        return self.log_folder_path + self.sep + self.current_err_log_file_name


def get_config() -> type[MainConfig]:
    """get db configuration"""
    return MainConfig
