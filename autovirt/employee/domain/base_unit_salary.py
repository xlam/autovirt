from dataclasses import dataclass


@dataclass
class BaseUnitSalary:
    SALARY_MARGIN = 5.0

    unit_id: int
    name: str
    city_name: str
    labor_max: int
    salary: float

    def __post_init__(self):
        self.initial_salary = self.salary
