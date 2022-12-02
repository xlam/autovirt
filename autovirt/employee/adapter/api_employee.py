from autovirt.employee.action.gateway import EmployeeGateway
from autovirt.employee.domain import DemandingUnitSalary
from autovirt.employee.domain import RequiringUnitSalary
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

    def get_units_requiring_salary_raise(self) -> list[RequiringUnitSalary]:
        employee_by_units = self.get_employee_by_units()
        units: list[RequiringUnitSalary] = []
        for unit in employee_by_units:
            if float(unit["employee_level_required"]) > float(unit["labor_level"]):
                unit_info = self.get_unit_info(int(unit["id"]))
                units.append(
                    RequiringUnitSalary(
                        int(unit["id"]),
                        unit["name"],
                        unit["city_name"],
                        int(unit["labor_max"]),
                        float(unit["labor_salary"]),
                        unit_info["salary_required"],
                    )
                )
        return units

    def get_units_demanding_salary_raise(self) -> list[DemandingUnitSalary]:
        employee_by_recruiting = self.get_employee_by_recruiting()
        units = []
        for unit in employee_by_recruiting:
            units.append(
                DemandingUnitSalary(
                    int(unit["id"]),
                    unit["name"],
                    unit["city_name"],
                    int(unit["labor_max"]),
                    float(unit["salary"]),
                    float(unit["last_salary_requirements"]),
                )
            )
        return [u for u in units if u.last_salary_requirements > u.salary]

    def set_salary(self, unit_id: int, employee_count: int, salary: float):
        self.s.post(
            f"https://virtonomica.ru/api/vera/main/unit/employee/update",
            {
                "id": unit_id,
                "employee_count": employee_count,
                "employee_salary": salary,
                "token": self.s.token,
            },
        )
