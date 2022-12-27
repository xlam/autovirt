from dataclasses import dataclass, field
from autovirt.exception import AutovirtError


class SupplyNotFound(AutovirtError):
    pass


@dataclass
class SupplyContract:
    consumer_id: int
    offer_id: int
    supplier_id: int
    free_for_buy: int
    party_quantity: int


@dataclass
class Supply:
    unit_id: int
    product_id: int
    product_name: str
    quantity: int
    required: int
    contracts: list[SupplyContract] = field(default_factory=list)

    @property
    def ordered(self) -> int:
        return sum(contract.party_quantity for contract in self.contracts)

    def _set_contracts(self, quantity):
        total_free_for_buy = sum(contract.free_for_buy for contract in self.contracts)
        for contract in self.contracts:
            contract.party_quantity = (
                int(contract.free_for_buy / total_free_for_buy * quantity)
                if total_free_for_buy
                else 0
            )

    def set_order_quantity_by_target_quantity(self, target_quantity):
        if self.quantity <= target_quantity:
            self._set_contracts(target_quantity)
        else:
            self._set_contracts(max(0, target_quantity - self.quantity + self.required))

    def set_order_quantity_by_factor_of_required(self, factor: int = 1):
        required = self.required * factor
        if self.quantity > required:
            self._set_contracts(0)
        else:
            self._set_contracts(required)


class UnitSupplies(list):
    def __init__(self, unit_id: int, items: list[Supply] = None):
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

    def get_contracts_by_product_id(self, product_id: int) -> list[SupplyContract]:
        return self.get_supply_by_product_id(product_id).contracts
