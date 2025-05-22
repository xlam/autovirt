from autovirt.employee.action.gateway import EmployeeGateway
from autovirt.employee.domain.demanding_unit import DemandingUnit
from autovirt.utils import get_logger


class SetDemandedSalaryInstrumentation:
    def __init__(self):
        self.logger = get_logger()

    def no_units_to_set_salary(self):
        self.logger.info("No units to set demanded salary, exiting.")

    def setting_salary(self, unit: DemandingUnit):
        self.logger.info(
            f"Raising salary at {unit.name} ({unit.id}), {unit.city_name} "
            f"from {unit.initial_salary} to {unit.salary}"
        )


class SetDemandedSalaryAction:
    def __init__(self, employee_gateway: EmployeeGateway, dry_run: bool = False):
        self.employee_gateway = employee_gateway
        self.instrumentation = SetDemandedSalaryInstrumentation()
        self.dry_run = dry_run

    def run(self):
        units = self.employee_gateway.get_units_demanding_salary_raise()
        if not units:
            self.instrumentation.no_units_to_set_salary()

        for unit in units:
            unit.set_demanded_salary()
            self.instrumentation.setting_salary(unit)
            if not self.dry_run:
                self.employee_gateway.set_salary(unit)
