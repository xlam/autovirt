from dataclasses import dataclass

from .unit import Unit


@dataclass
class RequiringUnit(Unit):
    salary_required: float

    def set_required_salary(self):
        self.salary = int(self.salary_required + self.SALARY_MARGIN)
