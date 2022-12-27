import pytest

from autovirt.exception import AutovirtError
from autovirt.logistics.action.free_shop_storage import FreeShopStorageAction
from autovirt.logistics.action.gateway.shop import ShopGateway
from autovirt.logistics.domain.delivery import Delivery
from autovirt.logistics.domain.unit_product import UnitProduct
from autovirt.logistics.domain.warehouse import Warehouse


class FakeShopAdapter(ShopGateway):
    def __init__(self):
        self.delivered = []

    def get_shop_products(self, unit_id) -> list[UnitProduct]:
        return [
            UnitProduct(1, "Product1", unit_id, 1000, 100),
            UnitProduct(2, "Product2", unit_id, 1000, 1000),
            UnitProduct(3, "Product3", unit_id, 100, 1000),
        ]

    def get_warehouses_for(self, product: UnitProduct) -> list[Warehouse]:
        return [
            Warehouse(1, 1000, 5.0),
            Warehouse(2, 5000, 10.0),
            Warehouse(3, 0, 1.0),
        ]

    def set_delivery(self, delivery: Delivery):
        self.delivered.append(delivery)


def test_free_storage_action():
    shop_gateway = FakeShopAdapter()
    action = FreeShopStorageAction(shop_gateway)
    deliveries = action.run(unit_id=1)
    assert len(deliveries) == 1
    assert deliveries[0].product_id == 1
    assert deliveries[0].to_unit_id == 2
    assert deliveries[0].quantity == 800


def test_exception_if_there_are_no_suitable_warehouses_for_product_delivery():
    shop_gateway = FakeShopAdapter()
    shop_gateway.get_warehouses_for = lambda x: []  # mock to return empty list
    action = FreeShopStorageAction(shop_gateway)
    with pytest.raises(AutovirtError):
        action.run(unit_id=1)
