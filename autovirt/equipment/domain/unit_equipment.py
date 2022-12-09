from dataclasses import dataclass
from math import ceil

FLOAT_PRECISION = 2


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

    def __post_init__(self):
        self.quality = round(self.quality, FLOAT_PRECISION)
        self.quality_required = round(self.quality_required, FLOAT_PRECISION)

    def expected_quality(self, repair_quality: float):
        return (
            self.quality * (self.quantity - self.wear_quantity)
            + repair_quality * self.wear_quantity
        ) / self.quantity
