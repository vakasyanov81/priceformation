"""
test init_log
"""

from typing import Any
from unittest.mock import patch

import pytest

from core.init_log import (
    create_logs_folder,
    create_logs_folder_if_not_exists,
    folder_is_exists,
    init_log,
)

_FOLDER = "~/some_folder/"


def test_init_log() -> None:
    """test init log"""

    with patch("core.init_log.create_logs_folder_if_not_exists") as mock_create_logs_folder:
        init_log()

    assert mock_create_logs_folder.call_count == 1
    assert mock_create_logs_folder.call_args[0][0] is not None


@patch("pathlib.Path.mkdir")
def test_create_logs_folder(mock_os_mkdir: Any) -> None:
    """test create logs folder"""

    create_logs_folder(_FOLDER)
    assert mock_os_mkdir.call_count == 1


@patch("pathlib.Path.is_dir")
@pytest.mark.parametrize("folder_is_exist", [True, False])
def test_folder_is_exists(mock_os_isdir: Any, folder_is_exist: Any) -> None:
    """test folder is exists"""

    mock_os_isdir.return_value = folder_is_exist
    folder_exists = folder_is_exists(_FOLDER)

    assert mock_os_isdir.call_count == 1
    assert folder_exists == folder_is_exist


@patch("core.init_log.folder_is_exists")
@pytest.mark.parametrize("folder_is_exist, folder_created", [(True, False), (False, True)])
def test_create_logs_folder_if_not_exists(
    mock_folder_is_exists: Any, folder_is_exist: Any, folder_created: Any
) -> None:
    """test create logs folder if not exists"""

    mock_folder_is_exists.return_value = folder_is_exist

    with patch("core.init_log.create_logs_folder", return_value=True):
        folder_created_flag = create_logs_folder_if_not_exists(_FOLDER)

    assert mock_folder_is_exists.call_count == 1
    assert folder_created_flag == folder_created
