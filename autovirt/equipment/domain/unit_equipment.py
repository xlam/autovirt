from dataclasses import dataclass
from math import ceil


@dataclass
class UnitEquipment:
    id: int
    quantity: int
    quantity_max: int
    quality: float
    quality_required: float
    wear: float
    equipment_id: int

    @property
    def wear_quantity(self) -> int:
        return ceil(self.quantity * self.wear * 0.01)

    def expected_quality(self, repair_quality: float):
        return (
            self.quality * (self.quantity - self.wear_quantity)
            + repair_quality * self.wear_quantity
        ) / self.quantity
