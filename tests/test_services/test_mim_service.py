"""MimService: выгрузка каталога МИМ по API."""

from unittest.mock import MagicMock, patch

import pytest

from infrastructure.config.mim_api_config import MimApiConfig
from parsers.remote.mim_client import MimApiRequest
from parsers.vendor_config.models import VendorConfig
from parsers.vendor_config.slot_configs import BehaviorConfig
from services.mim_service import MimService

_API = MimApiConfig(host='h', token='t')


def _upload(configs: dict[str, VendorConfig]) -> MimApiRequest:
    with (
        patch('services.mim_service.get_mim_api_config', return_value=_API),
        patch('services.mim_service.load_vendor_configs', return_value=configs),
        patch('services.mim_service.load_remote_vendor_data') as mock_load,
    ):
        MimService().upload_data()
    request: MimApiRequest = mock_load.call_args.kwargs['api']
    return request


def _vendor(api_types: tuple[int, ...]) -> VendorConfig:
    return MagicMock(spec=VendorConfig, behavior=BehaviorConfig(api_types=api_types))


def test_upload_data_takes_types_from_vendor_config() -> None:
    request = _upload({'mim': _vendor((2, 4))})

    assert request == MimApiRequest(host='h', token='t', types=(2, 4))


@pytest.mark.parametrize('configs', [{}, {'other': MagicMock(spec=VendorConfig)}])
def test_upload_data_default_types(configs: dict[str, VendorConfig]) -> None:
    assert _upload(configs).types == (1, 3, 4)
