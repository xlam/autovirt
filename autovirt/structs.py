from dataclasses import dataclass
from math import ceil

# Virtonomica provide high precision numbers that we don't need (2 digits round is ok)
FLOAT_PRECISION = 2


@dataclass
class UnitEquipment:
    id: int
    qnt: int
    qnt_max: int
    qual: float
    qual_req: float
    wear: float
    equipment_id: int

    @property
    def wear_quantity(self) -> int:
        return ceil(self.qnt * self.wear * 0.01)

    def __post_init__(self):
        self.qual = round(self.qual, FLOAT_PRECISION)
        self.qual_req = round(self.qual_req, FLOAT_PRECISION)

    def expected_quality(self, repair_quality: float):
        return (
            self.qual * (self.qnt - self.wear_quantity)
            + repair_quality * self.wear_quantity
        ) / self.qnt


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
