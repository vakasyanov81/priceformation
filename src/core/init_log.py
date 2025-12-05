"""
init log folder logic
"""

from pathlib import Path

from cfg import init_cfg


def init_log():
    """initialize log system"""
    create_logs_folder_if_not_exists(init_cfg().main.log_folder_path)


def create_logs_folder_if_not_exists(log_folder) -> bool:
    """create logs folder if it not exists"""
    if not folder_is_exists(log_folder):
        return create_logs_folder(log_folder)
    return False


def folder_is_exists(folder):
    """folder is exists?"""
    return Path(folder).is_dir()


def create_logs_folder(log_folder):
    """create logs folder"""
    Path(log_folder).mkdir()
    return True


__ALL__ = [init_log]
