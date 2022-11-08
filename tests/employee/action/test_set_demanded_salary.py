from autovirt.employee.action import SetDemandedSalaryAction
from autovirt.employee.action.gateway import EmployeeGateway
from autovirt.employee.domain import DemandingUnitSalary


class FakeEmployeeAdapter(EmployeeGateway):
    def __init__(self):
        self.units: dict = {
            1: DemandingUnitSalary(1, "unit1", "city1", 1000, 100, 200),
            2: DemandingUnitSalary(2, "unit2", "city2", 1000, 100, 0),
            3: DemandingUnitSalary(3, "unit3", "city3", 1000, 100, 300),
        }

    def get_units_demanding_salary_raise(self) -> list[DemandingUnitSalary]:
        return [
            unit
            for unit in self.units.values()
            if unit.last_salary_requirements > unit.salary
        ]

    def set_salary(self, unit_id: int, employee_count: int, salary: float):
        self.units[unit_id].salary = salary


def test_set_demanded_salary():
    gw = FakeEmployeeAdapter()
    action = SetDemandedSalaryAction(gw)
    action.run()
    assert len(gw.get_units_demanding_salary_raise()) == 0
