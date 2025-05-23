from dataclasses import dataclass

ORDER_MULTIPLIER = 2


@dataclass(frozen=True)
class Product:
    id: int
    name: str
    unit_id: int
    quantity: int
    order_amount: int

    @property
    def extra_quantity(self) -> int:
        if self.order_amount > 0:
            return max(0, self.quantity - self.order_amount * ORDER_MULTIPLIER)
        return 0
