from dataclasses import dataclass

from .base_unit_salary import BaseUnitSalary


@dataclass
class DemandingUnitSalary(BaseUnitSalary):
    last_salary_requirements: float

    def set_demanded_salary(self):
        if self.last_salary_requirements > 0:
            self.salary = int(self.last_salary_requirements + self.SALARY_MARGIN)
