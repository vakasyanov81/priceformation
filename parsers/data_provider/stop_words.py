# -*- coding: utf-8 -*-
"""
stop words provider
"""
__author__ = "Kasyanov V.A."

from cfg.main import MainConfig
from core.file_reader import read_file

from .black_list import BlackListProviderFromUserConfig


class StopWordsProviderBase:
    """Base stop words data provider"""

    def get_stop_words_data(self):
        """Abstract method. Get stop words data."""
        raise NotImplementedError


class StopWordsProviderFromUserConfig(StopWordsProviderBase):
    """Stop words data provider from user config file."""

    def get_stop_words_data(self):
        """Get stop words"""
        return BlackListProviderFromUserConfig.split_and_filtration(
            read_file(MainConfig().stop_words_file_path)
        )
