from typing import Protocol

from autovirt.sales.domain import Product


class SalesGateway(Protocol):
    def get_shop_products(self, shop_id) -> list[Product]:
        ...

    def update_price_for(self, product: Product):
        ...
