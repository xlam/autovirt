from typing import Protocol


class EmployeeInterface(Protocol):
    def units(self) -> list:
        ...

    def unit_info(self, unit_id: int) -> dict:
        ...

    def set_salary(self, unit_id: int, employee_count: int, salary: float):
        ...
