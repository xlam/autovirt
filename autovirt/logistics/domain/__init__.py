from autovirt.logistics.domain.product import Product
from autovirt.logistics.domain.warehouse import Warehouse


def choose_warehouse(warehouses: list[Warehouse]) -> Warehouse:
    return sorted(warehouses, key=lambda x: x.quantity)[-1]
