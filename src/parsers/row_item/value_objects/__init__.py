"""Value Object dataclasses для RowItem."""

from parsers.row_item.value_objects.disk_parameters import DiskParameters
from parsers.row_item.value_objects.duplicate_info import DuplicateInfo
from parsers.row_item.value_objects.pricing import Pricing
from parsers.row_item.value_objects.product_identity import ProductIdentity
from parsers.row_item.value_objects.tire_dimensions import TireDimensions

__all__ = [
    'DiskParameters',
    'DuplicateInfo',
    'Pricing',
    'ProductIdentity',
    'TireDimensions',
]
