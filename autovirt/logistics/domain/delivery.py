from dataclasses import dataclass


@dataclass(frozen=True)
class Delivery:
    product_id: int
    product_name: str
    from_unit_id: int
    to_unit_id: int
    quantity: int
    item_cost: float

    @property
    def total_cost(self) -> float:
        return self.quantity * self.item_cost
