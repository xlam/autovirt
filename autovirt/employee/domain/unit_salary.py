from dataclasses import dataclass
from typing import Optional

SALARY_MARGIN: float = 5.0
""" Salary margin to add to demanded salary value"""


@dataclass
class UnitSalary:
    unit_id: int
    name: str
    city_name: str
    labor_max: int
    salary: float
    last_salary_requirements: float


def set_demanded_salary(unit: UnitSalary) -> Optional[float]:
    if unit.last_salary_requirements > 0:
        initial_salary = unit.salary
        unit.salary = int(unit.last_salary_requirements + SALARY_MARGIN)
        return initial_salary
    return None
