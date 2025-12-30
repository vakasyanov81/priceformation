from typing import Literal
from .zapaska_tire_data_factory import get_vendor_params as get_zapaska_tire_params

def get_vendor_params(vendor_name: Literal['zapaska_tire']):
    mapping = {
        'zapaska_tire': get_zapaska_tire_params
    }
    params = mapping.get(vendor_name) if mapping.get(vendor_name) else {}
    return params
__ALL__ = [get_vendor_params]