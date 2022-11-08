from typing import Protocol

from autovirt.employee.domain.demanding_unit_salary import DemandingUnitSalary
from autovirt.employee.domain.requiring_unit_salary import RequiringUnitSalary


class EmployeeGateway(Protocol):
    def get_units_requiring_salary_raise(self) -> list[RequiringUnitSalary]:
        ...

    def get_units_demanding_salary_raise(self) -> list[DemandingUnitSalary]:
        ...

    def set_salary(self, unit_id: int, employee_count: int, salary: float):
        ...
