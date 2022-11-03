from autovirt.employee.domain.unit_salary import UnitSalary
from autovirt.session import VirtSession
from autovirt.virtapi import GatewayOptions


class UnitSalaryAdapter:
    def __init__(self, session: VirtSession, options: GatewayOptions):
        self.s = session
        self.options = options

    def get_units_demanding_salary_raise(self) -> list[UnitSalary]:
        r = self.s.get(
            "https://virtonomica.ru/api/vera/main/company/employee/recruiting",
            params={"id": self.options.company_id, "pagesize": self.options.pagesize},
        )
        units = []
        for unit in list(r.json()["data"].values()):
            units.append(
                UnitSalary(
                    int(unit["id"]),
                    unit["name"],
                    unit["city_name"],
                    int(unit["labor_max"]),
                    float(unit["salary"]),
                    float(unit["last_salary_requirements"]),
                )
            )
        return [u for u in units if u.last_salary_requirements > u.salary]

    def set_salary(self, units: list[UnitSalary]):
        for unit in units:
            self.s.post(
                f"https://virtonomica.ru/api/vera/main/unit/employee/update",
                {
                    "id": unit.unit_id,
                    "employee_count": unit.labor_max,
                    "employee_salary": unit.salary,
                    "token": self.s.token,
                },
            )
