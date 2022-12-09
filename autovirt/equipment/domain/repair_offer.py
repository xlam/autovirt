from dataclasses import dataclass


@dataclass()
class RepairOffer:
    id: int
    company_id: int
    company_name: str
    price: float
    quality: float
    quantity: int

    @property
    def qp_ratio(self) -> float:
        return self.quality / self.quantity
