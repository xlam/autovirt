from typing import Optional

from autovirt import utils
from autovirt.employee.action.gateway import EmployeeGateway

logger = utils.get_logger()


class SetDemandedSalaryAction:
    def __init__(self, employee_gateway: EmployeeGateway):
        self.employee_gateway = employee_gateway

    def run(self, config_name: Optional[str] = None):
        if not config_name:
            pass

        units = self.employee_gateway.get_units_demanding_salary_raise()
        if not units:
            logger.info("no units to set demanded salary, exiting.")
            return

        for unit in units:
            unit.set_demanded_salary()
            logger.info(
                f"raising salary at {unit.name} ({unit.unit_id}), {unit.city_name} "
                f"from {unit.initial_salary} to {unit.salary}"
            )
            self.employee_gateway.set_salary(unit.unit_id, unit.labor_max, unit.salary)
