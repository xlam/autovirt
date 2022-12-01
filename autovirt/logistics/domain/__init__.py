from autovirt.logistics.domain.unitproduct import UnitProduct
from autovirt.logistics.domain.warehouse import Warehouse


def choose_warehouse(available_warehouses: list[Warehouse]) -> Warehouse:
    return sorted(available_warehouses, key=lambda x: x.quantity)[-1]


def get_extra_quantity(product: UnitProduct) -> int:
    if product.order_amount > 0:
        return max(0, product.quantity - product.order_amount * 2)
    return 0
