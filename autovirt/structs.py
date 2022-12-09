from dataclasses import dataclass

from autovirt.equipment.domain.unit_equipment import FLOAT_PRECISION


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


@dataclass
class Message:
    id: int
    subject: str
    body: str
    status: int
    attaches: list[dict]
