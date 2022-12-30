from .warehouse import Warehouse
from .product import Product


def choose_warehouse(warehouses: list[Warehouse]) -> Warehouse:
    return sorted(warehouses, key=lambda x: x.quantity)[-1]


def filter_extra_quantity(products: list[Product]) -> list[Product]:
    return [p for p in products if p.extra_quantity > 0]
