from dataclasses import dataclass

from autovirt.equipment.domain.unit_equipment import FLOAT_PRECISION


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

    def __post_init__(self):
        self.price = round(self.price, FLOAT_PRECISION)
        self.quality = round(self.quality, FLOAT_PRECISION)
