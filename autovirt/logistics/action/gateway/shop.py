from typing import Protocol

from autovirt.logistics.domain.delivery import Delivery
from autovirt.logistics.domain.unit_product import UnitProduct
from autovirt.logistics.domain.warehouse import Warehouse


class ShopGateway(Protocol):
    def get_shop_products(self, unit_id: int) -> list[UnitProduct]:
        ...

    def get_warehouses_for(self, product: UnitProduct) -> list[Warehouse]:
        ...

    def set_delivery(self, delivery: Delivery):
        ...
