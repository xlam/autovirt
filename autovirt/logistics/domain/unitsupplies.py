from dataclasses import dataclass, field


@dataclass
class SupplyContract:
    consumer_id: int
    offer_id: int
    supplier_id: int
    free_for_buy: int
    party_quantity: int


@dataclass
class Supply:
    product_id: int
    quantity: int
    required: int
    contracts: list[SupplyContract] = field(default_factory=list)

    @property
    def ordered(self) -> int:
        return sum(contract.party_quantity for contract in self.contracts)

    def set_order_by_required_factor(self, factor: int = 1):
        if self.quantity > self.required * factor:
            for contract in self.contracts:
                contract.party_quantity = 0
        else:
            total_free_for_buy = sum(
                contract.free_for_buy for contract in self.contracts
            )
            for contract in self.contracts:
                contract.party_quantity = (
                    contract.free_for_buy / total_free_for_buy * self.required * factor
                )


class UnitSupplies(list):
    def __init__(self, items: list[Supply] = None):
        items = items if items else []
        list.__init__(self, items)

    def get_supply_by_product_id(self, product_id: int) -> Supply:
        for item in self:
            if item.product_id == product_id:
                return item
        raise IndexError(f"Supply for product_id={product_id} is not found")

    def get_contracts_by_product_id(self, product_id: int) -> list[SupplyContract]:
        return self.get_supply_by_product_id(product_id).contracts
