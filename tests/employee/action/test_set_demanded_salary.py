from autovirt.employee.action import SetDemandedSalaryAction
from autovirt.employee.action.gateway import EmployeeGateway
from autovirt.employee.domain.demanding_unit import DemandingUnit
from autovirt.employee.domain.unit import Unit


class FakeEmployeeAdapter(EmployeeGateway):
    def __init__(self):
        self.units: dict = {
            1: DemandingUnit(1, "unit1", "city1", 1000, 100, 200),
            2: DemandingUnit(2, "unit2", "city2", 1000, 100, 0),
            3: DemandingUnit(3, "unit3", "city3", 1000, 100, 300),
        }

    def get_units_demanding_salary_raise(self) -> list[DemandingUnit]:
        return [
            unit
            for unit in self.units.values()
            if unit.last_salary_requirements > unit.salary
        ]

    def set_salary(self, unit_salary: Unit):
        self.units[unit_salary.id].salary = unit_salary.salary


def test_set_demanded_salary():
    gw = FakeEmployeeAdapter()
    action = SetDemandedSalaryAction(gw)
    action.run()
    assert len(gw.get_units_demanding_salary_raise()) == 0
