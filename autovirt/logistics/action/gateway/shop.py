from typing import Protocol

from autovirt.logistics.domain.storage.delivery import Delivery
from autovirt.logistics.domain.storage.product import Product
from autovirt.logistics.domain.storage.warehouse import Warehouse


class ShopGateway(Protocol):
    def get_shop_products(self, unit_id: int) -> list[Product]:
        ...

    def get_warehouses_for(self, product: Product) -> list[Warehouse]:
        ...

    def set_delivery(self, delivery: Delivery):
        ...
