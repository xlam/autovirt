from autovirt.employee.interface import EmployeeGateway
from autovirt.session import VirtSession
from autovirt.virtapi import GatewayOptions


class VirtEmployee(EmployeeGateway):
    def __init__(self, session: VirtSession, options: GatewayOptions):
        self.s = session
        self.options = options

    def units(self) -> list:
        r = self.s.get(
            "https://virtonomica.ru/api/vera/main/company/employee/units",
            params={"id": self.options.company_id, "pagesize": self.options.pagesize},
        )
        return list(r.json()["data"].values())

    def unit_info(self, unit_id: int) -> dict:
        r = self.s.get(
            "https://virtonomica.ru/api/vera/main/unit/employee/info",
            params={"id": unit_id},
        )
        return r.json()

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
