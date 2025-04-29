from typing import Union

from autovirt.exception import AutovirtError
from autovirt.logistics.domain.supplies.contract import Contract
from autovirt.logistics.domain.supplies.supply import Supply


class SupplyNotFound(AutovirtError):
    pass


class UnitSupplies(list):
    def __init__(self, unit_id: int, items: Union[list[Supply], None] = None):
        self.unit_id = unit_id
        items = items if items else []
        list.__init__(self, items)

    def append(self, supply: Supply) -> None:
        if self.unit_id == supply.unit_id:
            super(UnitSupplies, self).append(supply)

    def get_supply_by_product_id(self, product_id: int) -> Supply:
        for item in self:
            if item.product_id == product_id:
                return item
        raise SupplyNotFound(f"Supply for product_id={product_id} is not found")

    def get_contracts_by_product_id(self, product_id: int) -> list[Contract]:
        return self.get_supply_by_product_id(product_id).contracts
