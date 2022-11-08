from autovirt.employee.action import SetRequiredSalaryAction
from autovirt.employee.action.gateway import EmployeeGateway
from autovirt.employee.domain import RequiringUnitSalary


class FakeEmployeeAdapter(EmployeeGateway):
    def __init__(self):
        self.units: dict = {
            1: RequiringUnitSalary(1, "unit1", "city1", 1000, 100, 200),
            2: RequiringUnitSalary(2, "unit2", "city2", 1000, 100, 300),
        }

    def get_units_requiring_salary_raise(self) -> list[RequiringUnitSalary]:
        return [
            unit for unit in self.units.values() if unit.salary_required > unit.salary
        ]

    def set_salary(self, unit_id: int, employee_count: int, salary: float):
        self.units[unit_id].salary = salary


def test_set_required_salary():
    gw = FakeEmployeeAdapter()
    action = SetRequiredSalaryAction(gw)
    action.run()
    assert len(gw.get_units_requiring_salary_raise()) == 0
