"""
init log folder logic
"""

from pathlib import Path


def init_log(log_folder: str) -> None:
    """initialize log system"""
    create_logs_folder_if_not_exists(log_folder)


def create_logs_folder_if_not_exists(log_folder: str) -> bool:
    """create logs folder if it not exists"""
    if not folder_is_exists(log_folder):
        return create_logs_folder(log_folder)
    return False


def folder_is_exists(folder: str) -> bool:
    """folder is exists?"""
    return Path(folder).is_dir()


def create_logs_folder(log_folder: str) -> bool:
    """create logs folder"""
    Path(log_folder).mkdir()
    return True


__ALL__ = [init_log]
