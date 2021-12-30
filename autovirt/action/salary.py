from typing import Optional

from autovirt import utils
from autovirt.action.interface import EmployeeInterface

logger = utils.get_logger()


class SalaryAction:
    def __init__(self, employee_gateway: EmployeeInterface):
        self.employee = employee_gateway

    def units_to_update_salary(self) -> list[dict]:
        data = self.employee.units()
        units = []
        for unit in data:
            if float(unit["labor_level"]) < float(unit["employee_level_required"]):
                units.append(unit)
        return units

    def run(self, config_name: Optional[str] = None):
        if not config_name:
            pass

        units = self.units_to_update_salary()
        if not units:
            logger.info("no units to update salary, exiting.")
            quit(0)
        logger.info(f"{len(units)} units to update salary")

        for unit in units:
            unit_info = self.employee.unit_info(unit["id"])

            # set salary to required plus 5$ for sure
            salary = round(unit_info["salary_required"]) + 5

            logger.info(
                f"updating salary at unit "
                f"{unit['id']} ({unit['name']}, {unit['city_name']}) from "
                f"{unit['labor_salary']} to {salary}"
            )
            self.employee.set_salary(
                int(unit["id"]), int(unit_info["employee_max"]), salary
            )
