from typing import Optional

from autovirt import utils
from autovirt.employee.domain import units_to_update_salary
from autovirt.employee.action.gateway import EmployeeGateway

logger = utils.get_logger()


class SetRequiredSalaryAction:
    SALARY_MARGIN: float = 5.0
    """ Salary margin to add to required salary value"""

    def __init__(self, employee_gateway: EmployeeGateway):
        self.employee = employee_gateway

    def run(self, config_name: Optional[str] = None):
        if not config_name:
            pass

        units = units_to_update_salary(self.employee.units())
        if not units:
            logger.info("no units to update salary, exiting.")
            quit(0)
        logger.info(f"{len(units)} units to update salary")

        for unit in units:
            unit_info = self.employee.unit_info(unit["id"])

            # set salary to required plus 5$ for sure
            salary = round(unit_info["salary_required"]) + self.SALARY_MARGIN

            logger.info(
                f"updating salary at unit "
                f"{unit['id']} ({unit['name']}, {unit['city_name']}) from "
                f"{unit['labor_salary']} to {salary}"
            )
            self.employee.set_salary(
                int(unit["id"]), int(unit_info["employee_max"]), salary
            )
