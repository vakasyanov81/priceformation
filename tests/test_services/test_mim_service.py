"""MimService: выгрузка каталога МИМ по API."""

from unittest.mock import patch

from infrastructure.config.mim_api_config import MimApiConfig
from services.mim_service import MimService


def test_upload_data_passes_config_to_client() -> None:
    api = MimApiConfig(host='h', token='t', types=(1,))
    with (
        patch('services.mim_service.get_mim_api_config', return_value=api),
        patch('services.mim_service.load_remote_vendor_data') as mock_load,
    ):
        MimService().upload_data()

    mock_load.assert_called_once_with(api=api)
