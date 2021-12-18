from dataclasses import dataclass
from math import ceil

# Virtonomica provide high precision numbers that we don't need (2 digits round is ok)
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


@dataclass
class UnitEmployee:
    id: int
    employee_max: int
    employee_salary: float
    employee_level: float
    salary_required: float

    def __post_init__(self):
        self.employee_salary = round(self.employee_salary, FLOAT_PRECISION)
        self.employee_level = round(self.employee_level, FLOAT_PRECISION)
        self.salary_required = round(self.salary_required, FLOAT_PRECISION)


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


@dataclass
class Message:
    id: int
    subject: str
    body: str
    status: int
    attaches: list[dict]
