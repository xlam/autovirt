from dataclasses import dataclass
from math import ceil


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


@dataclass
class UnitEmployee:
    id: int
    employee_max: int
    employee_salary: float
    employee_level: float
    salary_required: float


@dataclass
class RepairOffer:
    id: int
    price: float
    quality: float
    quantity: int


@dataclass
class Message:
    id: int
    subject: str
    body: str
    status: int
    attaches: list[dict]
