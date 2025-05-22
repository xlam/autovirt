from autovirt.sales.action.gateway.sales import SalesGateway
from autovirt.sales.domain import Product, RetailPriceCalculator
from autovirt.utils import get_logger


class ManageRetailPricesInstrumentation:
    def __init__(self):
        self.logger = get_logger()

    def price_calculated(self, product: Product, old_price: float):
        self.logger.info(
            f"Updating price of {product.name} ({product.id}) "
            f"from {old_price:.2f} to {product.price:.2f} (shop {product.shop_id})"
        )


class ManageRetailPricesAction:
    def __init__(self, sales_gateway: SalesGateway, dry_run: bool = False):
        self.sales_gateway = sales_gateway
        self.instrumentation = ManageRetailPricesInstrumentation()
        self.dry_run = dry_run

    def run(self, shop_id: int, method: RetailPriceCalculator) -> list[Product]:
        calculate_price = method
        updated_products: list[Product] = []
        products = self.sales_gateway.get_shop_products(shop_id)
        for product in products:
            old_price = product.price
            product.price = calculate_price(product)
            self.instrumentation.price_calculated(product, old_price)
            if not self.dry_run:
                self.sales_gateway.update_price_for(product)
            updated_products.append(product)
        return updated_products
