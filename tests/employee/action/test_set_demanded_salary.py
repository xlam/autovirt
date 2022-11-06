from autovirt.employee.action.gateway.unit_salary import UnitSalaryGateway
from autovirt.employee.action.set_demanded_salary import SetDemandedSalaryAction
from autovirt.employee.domain.unit_salary import UnitSalary


class FakeUnitSalaryAdapter(UnitSalaryGateway):
    def __init__(self):
        self.units = {
            1: UnitSalary(1, "unit1", "city1", 1000, 100, 200),
            2: UnitSalary(2, "unit2", "city2", 1000, 100, 0),
            3: UnitSalary(3, "unit3", "city3", 1000, 100, 300),
        }

    def get_units_demanding_salary_raise(self) -> list[UnitSalary]:
        return [
            unit
            for unit in self.units.values()
            if unit.last_salary_requirements > unit.salary
        ]

    def set_salary(self, units: list[UnitSalary]):
        for unit in units:
            self.units[unit.unit_id] = unit


def test_set_demanded_salary():
    gw = FakeUnitSalaryAdapter()
    action = SetDemandedSalaryAction(gw)
    action.run()
    assert len(gw.get_units_demanding_salary_raise()) == 0
