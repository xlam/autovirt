from dataclasses import dataclass, field

from autovirt.logistics.domain.supplies.contract import Contract


@dataclass
class Supply:
    unit_id: int
    product_id: int
    product_name: str
    quantity: int
    required: int
    contracts: list[Contract] = field(default_factory=list)

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
