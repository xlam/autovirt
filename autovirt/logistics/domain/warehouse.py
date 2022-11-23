from dataclasses import dataclass


@dataclass(frozen=True)
class Warehouse:
    id: int
    quantity: int
    delivery_cost: float
