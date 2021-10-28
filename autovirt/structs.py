from dataclasses import dataclass


@dataclass
class UnitEquipment:
    id: str
    qnt: str
    qnt_max: str
    qual: str
    qual_req: str
    wear: str
    equipment_id: str


@dataclass
class UnitEmployee:
    id: int
    employee_max: int
    employee_salary: float
    employee_level: float
    salary_required: float


@dataclass
class RepairOffer:
    id: str
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
