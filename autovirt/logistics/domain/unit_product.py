from dataclasses import dataclass


@dataclass(frozen=True)
class UnitProduct:
    id: int
    name: str
    unit_id: int
    quantity: int
    order_amount: int
