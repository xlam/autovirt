from typing import Protocol

from autovirt.employee.domain.demanding_unit import DemandingUnit
from autovirt.employee.domain.requiring_unit import RequiringUnit
from autovirt.employee.domain.unit import Unit


class EmployeeGateway(Protocol):
    def get_units_requiring_salary_raise(self) -> list[RequiringUnit]:
        ...

    def get_units_demanding_salary_raise(self) -> list[DemandingUnit]:
        ...

    def set_salary(self, unit_salary: Unit):
        ...
