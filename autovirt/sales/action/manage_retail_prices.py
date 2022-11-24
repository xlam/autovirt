from typing import Callable

from autovirt.sales.action.gateway.sales import SalesGateway
from autovirt.sales.domain import Product
from autovirt.utils import get_logger

logger = get_logger()


class ManageRetailPricesAction:
    def __init__(self, sales_gateway: SalesGateway):
        self.sales_gateway = sales_gateway

    def run(
        self, shop_id: int, method: Callable, dry_run: bool = False
    ) -> list[Product]:
        calculate_price = method
        updated_products: list[Product] = []
        products = self.sales_gateway.get_shop_products(shop_id)
        for product in products:
            old_price = product.price
            product.price = calculate_price(product)
            logger.info(
                f"Updating price of {product.name} ({product.id}) "
                f"from {old_price:.2f} to {product.price:.2f} (shop {product.shop_id})"
            )
            if not dry_run:
                self.sales_gateway.update_price_for(product)
            updated_products.append(product)
        return updated_products
