from typing import Optional

from autovirt import utils
from autovirt.employee.interface.unit_salary import UnitSalaryGateway
from autovirt.employee.domain.unit_salary import set_demanded_salary

logger = utils.get_logger()


class SetDemandedSalaryAction:
    def __init__(self, unit_salary_gateway: UnitSalaryGateway):
        self.unit_salary_gateway = unit_salary_gateway

    def run(self, config_name: Optional[str] = None):
        if not config_name:
            pass
        units = self.unit_salary_gateway.get_units_demanding_salary_raise()
        if not units:
            logger.info("no units to raise salary, exiting.")
            return
        for unit in units:
            initial_salary = set_demanded_salary(unit)
            logger.info(
                f"raising salary at {unit.name} ({unit.unit_id}), {unit.city_name} "
                f"from {initial_salary} to {unit.salary}"
            )
        self.unit_salary_gateway.set_salary(units)
