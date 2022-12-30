from autovirt.logistics.action.gateway.shop import ShopGateway
from autovirt.logistics.domain import choose_warehouse, filter_extra_quantity, Product
from autovirt.logistics.domain.delivery import Delivery
from autovirt.utils import get_logger


class FreeShopStorageInstrumentation:
    def __init__(self):
        self.logger = get_logger()

    def ready_to_deliver(self, delivery: Delivery):
        self.logger.info(
            f"Delivering {delivery.quantity} pieces of '{delivery.product_name}' ({delivery.product_id}) "
            f"from shop {delivery.from_unit_id} to warehouse {delivery.to_unit_id}, "
            f"delivery cost: {delivery.total_cost:.2f}"
        )

    def no_suitable_warehouse(self, product: Product):
        self.logger.warning(
            f"No suitable warehouses found for delivering "
            f"'{product.name}' ({product.id}) from unit {product.unit_id}"
        )


class FreeShopStorageAction:
    def __init__(self, shop_gateway: ShopGateway):
        self.shop_gateway = shop_gateway
        self.instrumentation = FreeShopStorageInstrumentation()

    def run(self, unit_id: int, dry_run: bool = False) -> list[Delivery]:
        deliveries = []
        produts = self.shop_gateway.get_shop_products(unit_id)
        produts = filter_extra_quantity(produts)
        for product in produts:
            available_warehouses = self.shop_gateway.get_warehouses_for(product)
            if not available_warehouses:
                self.instrumentation.no_suitable_warehouse(product)
                continue
            warehouse = choose_warehouse(available_warehouses)
            if warehouse:
                delivery = Delivery(
                    product.id,
                    product.name,
                    product.unit_id,
                    warehouse.id,
                    product.extra_quantity,
                    warehouse.delivery_cost,
                )
                self.instrumentation.ready_to_deliver(delivery)
                if not dry_run:
                    self.shop_gateway.set_delivery(delivery)
                deliveries.append(delivery)
        return deliveries
