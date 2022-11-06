from typing import Protocol

from autovirt.employee.domain.unit_salary import UnitSalary


class UnitSalaryGateway(Protocol):
    def get_units_demanding_salary_raise(self) -> list[UnitSalary]:
        ...

    def set_salary(self, units: list[UnitSalary]):
        ...
