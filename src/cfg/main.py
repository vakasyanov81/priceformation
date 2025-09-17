# -*- coding: utf-8 -*-
"""
main configuration
"""
__author__ = "Kasyanov V.A."

import datetime
import os
import pathlib

from .db import DBConfig
from .db import get_config as db_cfg

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

__IS_UNITTEST_MODE__ = False
__IS_NEED_PRINT_LOG__ = True


class MainCfg:
    """main configuration property container"""

    @property
    def folder_file_prices(self):
        """folder where vendor prices are stored"""
        return __FILE_PRICES__

    @property
    def folder_file_prices_result(self):
        """folder where price formation results are stored"""
        return f"{self.folder_file_prices}{os.sep}{__FILE_PRICES_RESULT__}"

    @property
    def vendor_list_file_name(self):
        """vendor list file name"""
        return __VENDOR_LIST_FILE_NAME__

    @property
    def markup_rules_file_name(self):
        """markup rules file name"""
        return __MARKUP_RULES_FILE_NAME__

    @property
    def black_list_file_name(self):
        """markup rules file name"""
        return __BLACK_LIST_FILE_NAME__

    @property
    def stop_words_file_name(self):
        """stop words file name"""
        return __STOP_WORDS_FILE_NAME__

    @property
    def user_config_folder_name(self):
        """folder name with user configuration"""
        return __USER_PARSE_CONFIG__

    @property
    def manufacturer_aliases_file_name(self):
        """..."""
        return __MANUFACTURER_ALIASES_FILE_NAME__

    @property
    def title_aliases_file_name(self):
        """..."""
        return __TITLE_ALIASES_FILE_NAME__

    @property
    def user_config_folder_path(self):
        """..."""
        return __PROJECT_ROOT__ + os.sep + self.user_config_folder_name + os.sep

    @property
    def manufacturer_aliases_file_path(self):
        """..."""
        return self.user_config_folder_path + self.manufacturer_aliases_file_name

    @property
    def title_aliases_file_path(self):
        """..."""
        return self.user_config_folder_path + self.title_aliases_file_name

    @property
    def markup_rules_file_path(self):
        """markup rules file"""
        return self.user_config_folder_path + self.markup_rules_file_name

    @property
    def black_list_file_path(self):
        """black list file"""
        return self.user_config_folder_path + self.black_list_file_name

    @property
    def stop_words_file_path(self):
        """stop words file"""
        return self.user_config_folder_path + self.stop_words_file_name

    @property
    def vendor_list_file_path(self):
        """path to vendor list file"""
        return self.user_config_folder_path + self.vendor_list_file_name


class MainConfig(MainCfg):
    """main configuration property container"""

    @property
    def project_root(self):
        """path to project root directory"""
        return __PROJECT_ROOT__

    @property
    def project_src(self):
        """path to project src directory"""
        return __PROJECT_SRC__

    @property
    def sep(self):
        """folder separator"""
        return os.sep

    @property
    def log_folder_name(self):
        """logs folder name"""
        return __LOG_FOLDER__

    @property
    def log_folder_path(self):
        """path to logs folder"""
        return self.project_root + self.sep + self.log_folder_name

    @property
    def current_log_file_name(self):
        """current log file name"""
        return f"log_{datetime.date.today()}.log"

    @property
    def current_err_log_file_name(self):
        """current log-error file name"""
        return f"error_{datetime.date.today()}.log"

    @property
    def current_log_file_path(self):
        """path to current log file"""
        return self.log_folder_path + self.sep + self.current_log_file_name

    @property
    def current_err_log_file_path(self):
        """path to current log-error file"""
        return self.log_folder_path + self.sep + self.current_err_log_file_name

    @property
    def is_need_print_log(self):
        """need show log on window via print() function"""
        return __IS_NEED_PRINT_LOG__

    @property
    def is_unittest_mode(self):
        """for mock in unittests run"""
        return __IS_UNITTEST_MODE__

    @classmethod
    def database(cls) -> DBConfig:
        """database config"""
        return db_cfg(__PROJECT_SRC__)


def get_config():
    """get db configuration"""
    return MainConfig
