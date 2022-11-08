from dataclasses import dataclass

from .base_unit_salary import BaseUnitSalary


@dataclass
class RequiringUnitSalary(BaseUnitSalary):
    salary_required: float

    def set_required_salary(self):
        self.salary = int(self.salary_required + self.SALARY_MARGIN)
