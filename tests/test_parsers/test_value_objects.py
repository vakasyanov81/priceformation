"""Тесты для value objects RowItem."""

from parsers.row_item.row_item import RowItem
from parsers.row_item.value_objects import (
    DiskParameters,
    DuplicateInfo,
    Pricing,
    ProductIdentity,
    TireDimensions,
)


class TestTireDimensions:
    """TireDimensions — габариты шины."""

    def test_defaults(self) -> None:
        dims = TireDimensions()
        assert dims.width == ''
        assert dims.height_percent == ''
        assert dims.diameter == ''
        assert dims.ext_diameter == 0

    def test_from_flat(self) -> None:
        dims = TireDimensions.from_flat(
            {
                'width': '205',
                'height_percent': '55',
                'diameter': '16',
                'ext_diameter': 0,
            }
        )
        assert dims.width == '205'
        assert dims.height_percent == '55'
        assert dims.diameter == '16'
        assert dims.ext_diameter == 0

    def test_from_flat_empty(self) -> None:
        dims = TireDimensions.from_flat({})
        assert dims.width == ''
        assert dims.height_percent == ''
        assert dims.diameter == ''
        assert dims.ext_diameter == 0

    def test_to_flat(self) -> None:
        dims = TireDimensions(width='205', height_percent='55', diameter='16', ext_diameter=33)
        flat = dims.to_flat()
        assert flat == {'width': '205', 'height_percent': '55', 'diameter': '16', 'ext_diameter': 33}

    def test_to_flat_roundtrip(self) -> None:
        original = TireDimensions(width='225', height_percent='45', diameter='17', ext_diameter=0)
        restored = TireDimensions.from_flat(original.to_flat())
        assert restored == original

    def test_bool(self) -> None:
        assert TireDimensions(width='205')
        assert TireDimensions(height_percent='55')
        assert TireDimensions(diameter='16')
        assert TireDimensions(ext_diameter=33)
        assert not TireDimensions()

    def test_ext_diameter_int_float(self) -> None:
        dims = TireDimensions(ext_diameter=33)
        assert dims.ext_diameter == 33
        dims = TireDimensions(ext_diameter=33.5)
        assert dims.ext_diameter == 33.5


class TestDiskParameters:
    """DiskParameters — параметры диска."""

    def test_defaults(self) -> None:
        dp = DiskParameters()
        assert dp.slot_count == 0
        assert dp.pcd1 == 0
        assert dp.pcd2 == 0
        assert dp.eet == 0
        assert dp.central_diameter == 0
        assert dp.disk_thickness == ''

    def test_from_flat(self) -> None:
        dp = DiskParameters.from_flat(
            {
                'slot_count': 5,
                'pcd1': 114.3,
                'pcd2': 0,
                'eet': 45,
                'central_diameter': 67.1,
                'disk_thickness': '15',
            }
        )
        assert dp.slot_count == 5
        assert dp.pcd1 == 114.3
        assert dp.eet == 45
        assert dp.central_diameter == 67.1
        assert dp.disk_thickness == '15'

    def test_from_flat_empty(self) -> None:
        dp = DiskParameters.from_flat({})
        assert dp.slot_count == 0

    def test_to_flat(self) -> None:
        dp = DiskParameters(slot_count=5, pcd1=114.3, eet=45, central_diameter=67.1)
        flat = dp.to_flat()
        assert flat['slot_count'] == 5
        assert flat['pcd1'] == 114.3
        assert flat['eet'] == 45

    def test_to_flat_roundtrip(self) -> None:
        original = DiskParameters(slot_count=5, pcd1=114.3, eet=45, central_diameter=67.1, disk_thickness='15')
        restored = DiskParameters.from_flat(original.to_flat())
        assert restored == original

    def test_pcd2(self) -> None:
        dp = DiskParameters(pcd2=100)
        assert dp.pcd2 == 100

    def test_bool(self) -> None:
        assert DiskParameters(slot_count=5)
        assert DiskParameters(pcd1=114.3)
        assert DiskParameters(disk_thickness='15')
        assert not DiskParameters()


class TestPricing:
    """Pricing — цены и наценки."""

    def test_defaults(self) -> None:
        p = Pricing()
        assert p.price_opt == 0
        assert p.price_recommended == 0
        assert p.price_markup == 0
        assert p.percent_markup == 0

    def test_from_flat(self) -> None:
        p = Pricing.from_flat(
            {
                'price_opt': 5000.50,
                'price_recommended': 6500.00,
                'price_markup': 5800.00,
                'percent_markup': 16.0,
            }
        )
        assert p.price_opt == 5000.50
        assert p.price_recommended == 6500.00
        assert p.price_markup == 5800.00
        assert p.percent_markup == 16.0

    def test_to_flat_roundtrip(self) -> None:
        original = Pricing(price_opt=1000, price_recommended=1500, price_markup=1200, percent_markup=20)
        restored = Pricing.from_flat(original.to_flat())
        assert restored == original

    def test_float_precision(self) -> None:
        p = Pricing(price_opt=99.99, percent_markup=5.5)
        assert p.price_opt == 99.99
        assert p.percent_markup == 5.5


class TestProductIdentity:
    """ProductIdentity — производитель, бренд, модель."""

    def test_defaults(self) -> None:
        pi = ProductIdentity()
        assert pi.manufacturer == ''
        assert pi.brand == ''
        assert pi.model == ''

    def test_from_flat_manufacturer_name_key(self) -> None:
        """Внутренний ключ manufacturer_name (FieldDescriptor)."""
        pi = ProductIdentity.from_flat(
            {
                'manufacturer_name': 'Bridgestone',
                'brand': 'Blizzak',
                'model': 'DM-V2',
            }
        )
        assert pi.manufacturer == 'Bridgestone'
        assert pi.brand == 'Blizzak'
        assert pi.model == 'DM-V2'

    def test_from_flat_manufacturer_key(self) -> None:
        """Запасной ключ manufacturer (прямой)."""
        pi = ProductIdentity.from_flat(
            {
                'manufacturer': 'Michelin',
                'brand': 'Pilot',
                'model': 'Sport 4',
            }
        )
        assert pi.manufacturer == 'Michelin'

    def test_to_flat(self) -> None:
        pi = ProductIdentity(manufacturer='Nokian', brand='Hakkapeliitta', model='R3')
        flat = pi.to_flat()
        assert flat == {'manufacturer_name': 'Nokian', 'brand': 'Hakkapeliitta', 'model': 'R3'}

    def test_to_flat_roundtrip(self) -> None:
        original = ProductIdentity(manufacturer='Continental', brand='VikingContact', model='7')
        restored = ProductIdentity.from_flat(original.to_flat())
        assert restored == original

    def test_codes_default(self) -> None:
        pi = ProductIdentity()
        assert pi.codes == []

    def test_manufacturer_fallback(self) -> None:
        """Если нет ни manufacturer ни manufacturer_name — пустая строка."""
        pi = ProductIdentity.from_flat({'brand': 'Test'})
        assert pi.manufacturer == ''


class TestDuplicateInfo:
    """DuplicateInfo — служебные поля дублей."""

    def test_defaults(self) -> None:
        di = DuplicateInfo()
        assert di.order == 0
        assert di.group_by_params == 0
        assert not di.is_double
        assert not di.double_candidate
        assert di.disputed == ''

    def test_from_flat(self) -> None:
        di = DuplicateInfo.from_flat(
            {
                'order': 1,
                'group_by_params': 42,
                'is_double': True,
                'double_candidate': False,
                'disputed': 'спор',
            }
        )
        assert di.order == 1
        assert di.group_by_params == 42
        assert di.is_double is True
        assert di.double_candidate is False
        assert di.disputed == 'спор'

    def test_to_flat_roundtrip(self) -> None:
        original = DuplicateInfo(order=5, group_by_params=100, is_double=True, disputed='цена')
        restored = DuplicateInfo.from_flat(original.to_flat())
        assert restored == original

    def test_bool_flags(self) -> None:
        di = DuplicateInfo(is_double=True, double_candidate=True)
        assert di.is_double is True
        assert di.double_candidate is True


class TestRowItemVOIntegration:
    """VO-свойства RowItem: чтение/запись через value objects."""

    def test_tire_read_write(self) -> None:
        r = RowItem({'width': '205', 'height_percent': '55', 'diameter': '16'})
        tire = r.tire
        assert isinstance(tire, TireDimensions)
        assert tire.width == '205'
        assert tire.height_percent == '55'
        assert tire.diameter == '16'

        r.tire = TireDimensions(width='225', height_percent='45', diameter='17')
        assert r.width == '225'
        assert r.height_percent == '45'
        assert r.diameter == '17'

    def test_disk_read_write(self) -> None:
        r = RowItem({'slot_count': 5, 'pcd1': 114.3, 'eet': 45})
        disk = r.disk
        assert isinstance(disk, DiskParameters)
        assert disk.slot_count == 5
        assert disk.pcd1 == 114.3

        r.disk = DiskParameters(slot_count=4, pcd1=100, eet=40, central_diameter=56.6)
        assert r.slot_count == 4
        assert r.pcd1 == 100

    def test_pricing_read_write(self) -> None:
        r = RowItem({'price_opt': 1000.0, 'price_recommended': 1500.0})
        pricing = r.pricing
        assert isinstance(pricing, Pricing)
        assert pricing.price_opt == 1000.0
        assert pricing.price_recommended == 1500.0

        r.pricing = Pricing(price_opt=2000, price_markup=2400, percent_markup=20)
        assert r.price_opt == 2000
        assert r.price_markup == 2400

    def test_product_identity_read_write(self) -> None:
        r = RowItem({'manufacturer_name': 'Bridgestone', 'brand': 'Blizzak', 'model': 'DM-V2'})
        pi = r.product_identity
        assert isinstance(pi, ProductIdentity)
        assert pi.manufacturer == 'Bridgestone'
        assert pi.brand == 'Blizzak'

        r.product_identity = ProductIdentity(manufacturer='Michelin', model='Pilot Sport')
        assert r.manufacturer == 'Michelin'

    def test_duplicate_read_write(self) -> None:
        r = RowItem({'order': 1, 'group_by_params': 42, 'is_double': True})
        dup = r.duplicate
        assert isinstance(dup, DuplicateInfo)
        assert dup.order == 1
        assert dup.group_by_params == 42
        assert dup.is_double is True

        r.duplicate = DuplicateInfo(order=10, group_by_params=99, is_double=True, disputed='цена')
        assert r.order == 10
        assert r.group_by_params == 99
        assert r.is_double is True

    def test_vo_mixed_with_flat(self) -> None:
        """Плоские и VO-свойства читают/пишут одно хранилище."""
        r = RowItem({'width': '205', 'price_opt': 5000})
        assert r.tire.width == '205'
        assert r.pricing.price_opt == 5000

        r.tire = TireDimensions(width='225')
        assert r.width == '225'

        r.pricing = Pricing(price_opt=6000)
        assert r.price_opt == 6000
