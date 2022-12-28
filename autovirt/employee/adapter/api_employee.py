from autovirt.employee.action.gateway import EmployeeGateway
from autovirt.employee.domain.demanding_unit import DemandingUnit
from autovirt.employee.domain.requiring_unit import RequiringUnit
from autovirt.employee.domain.unit import Unit
from autovirt.session import VirtSession
from autovirt.gateway_options import GatewayOptions


class ApiEmployeeAdapter(EmployeeGateway):
    def __init__(self, session: VirtSession, options: GatewayOptions):
        self.s = session
        self.options = options

    def get_employee_by_units(self) -> list:
        r = self.s.get(
            "https://virtonomica.ru/api/vera/main/company/employee/units",
            params={"id": self.options.company_id, "pagesize": self.options.pagesize},
        )
        return list(r.json()["data"].values())

    def get_employee_by_recruiting(self):
        r = self.s.get(
            "https://virtonomica.ru/api/vera/main/company/employee/recruiting",
            params={"id": self.options.company_id, "pagesize": self.options.pagesize},
        )
        return list(r.json()["data"].values())

    def get_unit_info(self, unit_id: int) -> dict:
        r = self.s.get(
            "https://virtonomica.ru/api/vera/main/unit/employee/info",
            params={"id": unit_id},
        )
        return r.json()

    def get_units_requiring_salary_raise(self) -> list[RequiringUnit]:
        employee_by_units = self.get_employee_by_units()
        units: list[RequiringUnit] = []
        for unit in employee_by_units:
            if float(unit["employee_level_required"]) > float(unit["labor_level"]):
                unit_info = self.get_unit_info(int(unit["id"]))
                units.append(
                    RequiringUnit(
                        int(unit["id"]),
                        unit["name"],
                        unit["city_name"],
                        int(unit["labor_max"]),
                        float(unit["labor_salary"]),
                        unit_info["salary_required"],
                    )
                )
        return units

    def get_units_demanding_salary_raise(self) -> list[DemandingUnit]:
        employee_by_recruiting = self.get_employee_by_recruiting()
        units = []
        for unit in employee_by_recruiting:
            units.append(
                DemandingUnit(
                    int(unit["id"]),
                    unit["name"],
                    unit["city_name"],
                    int(unit["labor_max"]),
                    float(unit["salary"]),
                    float(unit["last_salary_requirements"]),
                )
            )
        return [u for u in units if u.last_salary_requirements > u.salary]

    def set_salary(self, unit_salary: Unit):
        self.s.post(
            f"https://virtonomica.ru/api/vera/main/unit/employee/update",
            {
                "id": unit_salary.id,
                "employee_count": unit_salary.labor_max,
                "employee_salary": unit_salary.salary,
                "token": self.s.token,
            },
        )
