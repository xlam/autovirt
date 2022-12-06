from autovirt.logistics.action.gateway.shop import ShopGateway
from autovirt.logistics.domain import choose_warehouse, get_extra_quantity
from autovirt.logistics.domain.delivery import Delivery
from autovirt.exception import AutovirtError
from autovirt.utils import get_logger

logger = get_logger()


class FreeShopStorageAction:
    def __init__(self, shop_gateway: ShopGateway):
        self.shop_gateway = shop_gateway

    def run(self, unit_id: int, dry_run: bool = False) -> list[Delivery]:
        deliveries = []
        produts = self.shop_gateway.get_shop_products(unit_id)
        for product in produts:
            extra_quantity = get_extra_quantity(product)
            if extra_quantity > 0:
                available_warehouses = self.shop_gateway.get_warehouses_for(product)
                if not available_warehouses:
                    raise AutovirtError(
                        f"No suitable warehouses found for delivering '{product.name}' ({product.id}) from unit {product.unit_id}"
                    )
                warehouse = choose_warehouse(available_warehouses)
                if warehouse:
                    delivery = Delivery(
                        product.id,
                        product.name,
                        product.unit_id,
                        warehouse.id,
                        extra_quantity,
                        warehouse.delivery_cost,
                    )
                    if not dry_run:
                        self.shop_gateway.set_delivery(delivery)
                    deliveries.append(delivery)
        return deliveries
